"""Browser Action safety boundary (pure): allow-listed domains, allow-listed actions, never submits,
never touches OTP/CAPTCHA. Stops at Gate 4 (citizen does login/OTP/CAPTCHA)."""
from urllib.parse import urlparse

ALLOWED_ACTIONS = {"goto", "fill", "next"}
FORBIDDEN_TOKENS = ("submit", "captcha", "otp", "password")


class PortalViolation(Exception):
    pass


def validate_plan(plan: list, allowed_domains: tuple) -> None:
    for step in plan:
        action = step.get("action")
        if action not in ALLOWED_ACTIONS:
            raise PortalViolation(f"action '{action}' is not allowed")
        if action == "goto":
            host = urlparse(step.get("url", "")).hostname
            if host not in allowed_domains:
                raise PortalViolation(f"domain '{host}' is not on the allow-list")
        selector = str(step.get("selector", "")).lower()
        if any(tok in selector for tok in FORBIDDEN_TOKENS):
            raise PortalViolation(f"selector '{selector}' touches a forbidden control")


def build_plan(base_url: str, form: dict) -> list:
    plan = [{"action": "goto", "url": f"{base_url}/mock-portal/form"}]
    for field, value in form.items():
        plan.append({"action": "fill", "selector": f"[name={field}]", "value": str(value)})
    plan.append({"action": "next", "selector": "#continue"})
    return plan


def run_simulated(plan: list) -> list:
    log = []
    for s in plan:
        entry = {"action": s["action"], "target": s.get("selector") or s.get("url")}
        if s["action"] == "fill":
            entry["status"] = "filled"
        log.append(entry)
    log.append({"action": "handoff", "gate": 4,
                "message": "Paused. You must log in, complete OTP/CAPTCHA, review the form and click Submit yourself."})
    return log


def run_playwright(plan: list) -> list:  # pragma: no cover - needs a browser
    from playwright.sync_api import sync_playwright
    log = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for s in plan:
            if s["action"] == "goto":
                page.goto(s["url"], timeout=15000)
            elif s["action"] == "fill":
                page.fill(s["selector"], s["value"], timeout=5000)
            elif s["action"] == "next":
                page.click(s["selector"], timeout=5000)
            log.append({"action": s["action"], "target": s.get("selector") or s.get("url"), "status": "done"})
        browser.close()
    log.append({"action": "handoff", "gate": 4,
                "message": "Paused. You must log in, complete OTP/CAPTCHA, review the form and click Submit yourself."})
    return log
