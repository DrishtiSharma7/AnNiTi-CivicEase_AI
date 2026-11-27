"""Builds the SYNTHETIC labelled document set: images + data/labels.csv + data/meta.json.
Every image is watermarked 'SYNTHETIC DEMO DATA'. ID numbers are dummy values; labels keep only the last 4 digits.
Run: python synth/make_dataset.py [--people 12] [--seed 7]"""
import argparse
import csv
import json
import random
import sys
from datetime import date, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data"
FIRST = ["Ramesh", "Sunita", "Asha", "Mohan", "Kavita", "Imran", "Lakshmi", "Gurpreet", "Meena", "Anil", "Pooja", "Suresh"]
LAST = ["Kumar", "Devi", "Sharma", "Yadav", "Singh", "Khan", "Patel", "Reddy", "Verma", "Das", "Gupta", "Nair"]
INSTITUTIONS = ["Govt Senior Secondary School", "City Polytechnic", "Model Degree College"]
# condition -> what is wrong with this document (all other documents of the person are clean)
CONDITIONS = ["clear", "blurry", "cropped", "lowres", "expired", "expiring_soon", "name_mismatch", "missing_field"]


def font(size=22):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # old Pillow
        return ImageFont.load_default()


def render(title: str, lines: list) -> Image.Image:
    img = Image.new("RGB", (900, 620), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, 889, 609], outline="black", width=3)
    d.text((30, 25), "SYNTHETIC DEMO DATA - NOT A REAL DOCUMENT", fill=(200, 0, 0), font=font(22))
    d.text((30, 80), title, fill="black", font=font(34))
    y = 160
    for ln in lines:
        d.text((40, y), ln, fill="black", font=font(26))
        y += 58
    return img


def degrade(img: Image.Image, condition: str) -> Image.Image:
    if condition == "blurry":
        return img.filter(ImageFilter.GaussianBlur(7))
    if condition == "cropped":
        return img.crop((0, 0, int(img.width * 0.55), img.height))
    if condition == "lowres":
        return img.resize((150, 103)).resize((300, 206))
    return img


def build(people: int, seed: int, ref: date) -> tuple:
    rng = random.Random(seed)
    rows, names = [], set()
    for i in range(people):
        while True:
            name = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
            if name not in names:
                names.add(name)
                break
        pid = f"P{i + 1:02d}"
        dob = date(rng.randint(1950, 2005), rng.randint(1, 12), rng.randint(1, 28))
        id_digits = "9999" + "".join(rng.choice("0123456789") for _ in range(8))  # dummy, obviously fake prefix
        income = rng.choice([40000, 60000, 90000, 150000, 240000, 300000])
        # one condition per person, spread across the list so every condition appears
        cond = CONDITIONS[i % len(CONDITIONS)]
        for dtype in ("aadhaar", "income_certificate", "marksheet"):
            doc_cond = cond if (dtype == "income_certificate" or cond in ("blurry", "cropped", "lowres")) else "clear"
            if cond == "missing_field" and dtype != "aadhaar":
                doc_cond = "clear"
            if cond == "missing_field" and dtype == "aadhaar":
                doc_cond = "missing_field"
            fields = {"name": name}
            doc_name = name
            if dtype == "aadhaar":
                fields.update(dob=dob.isoformat(), id_last4=id_digits[-4:])
            elif dtype == "income_certificate":
                valid = ref + timedelta(days=rng.randint(120, 400))
                if doc_cond == "expired":
                    valid = ref - timedelta(days=rng.randint(10, 120))
                elif doc_cond == "expiring_soon":
                    valid = ref + timedelta(days=rng.randint(3, 25))
                if doc_cond == "name_mismatch":
                    doc_name = f"{name.split()[0][:3]}. {name.split()[1]}"  # e.g. "Ram. Kumar"
                fields.update(name=doc_name, annual_income=income, valid_until=valid.isoformat())
            else:
                fields.update(institution=rng.choice(INSTITUTIONS))
            if doc_cond == "missing_field":
                fields.pop("dob", None)
            # expected findings for this document, derived from the rules in plain sight (not from the engine)
            exp = set()
            if doc_cond == "expired":
                exp.add("EXPIRED")
            if doc_cond == "expiring_soon":
                exp.add("EXPIRING_SOON")
            if doc_cond == "name_mismatch" and dtype == "income_certificate":
                exp.add("NAME_MISMATCH")
            if doc_cond == "missing_field":
                exp.add("MISSING_FIELD")
            quality = {"blurry": "blurry", "cropped": "cropped", "lowres": "blurry"}.get(doc_cond, "clear")
            if quality == "blurry":
                exp.add("QUALITY_BLURRY")
            if quality == "cropped":
                exp.add("QUALITY_CROPPED")
            lines = [f"Name: {fields['name']}"]
            if dtype == "aadhaar":
                lines += [f"DOB: {fields.get('dob', '')}", f"ID: {id_digits[:4]} {id_digits[4:8]} {id_digits[8:]}"]
            elif dtype == "income_certificate":
                lines += [f"Annual income: Rs {income}", f"Valid until: {fields['valid_until']}"]
            else:
                lines += [f"Institution: {fields['institution']}"]
            fname = f"{pid}_{dtype}_{doc_cond}.png"
            img = degrade(render(dtype.replace("_", " ").title(), lines), doc_cond)
            (OUT / "documents").mkdir(parents=True, exist_ok=True)
            img.save(OUT / "documents" / fname)
            rows.append({
                "doc_id": f"{pid}_{dtype}", "file": f"documents/{fname}", "person_id": pid, "doc_type": dtype,
                "condition": doc_cond, "name": fields["name"], "dob": fields.get("dob", ""),
                "id_last4": fields.get("id_last4", ""), "annual_income": fields.get("annual_income", ""),
                "valid_until": fields.get("valid_until", ""), "institution": fields.get("institution", ""),
                "quality": quality, "expected_findings": "|".join(sorted(exp)),
            })
    return rows, {"reference_date": ref.isoformat(), "seed": seed, "people": people, "synthetic": True}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--people", type=int, default=16)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--reference-date", default="2026-11-20", help="expiry checks run 'as of' this date (keeps runs repeatable)")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    rows, meta = build(a.people, a.seed, date.fromisoformat(a.reference_date))
    with open(OUT / "labels.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2))
    print(f"wrote {len(rows)} labelled documents for {a.people} synthetic people -> {OUT}")


if __name__ == "__main__":
    sys.exit(main())
