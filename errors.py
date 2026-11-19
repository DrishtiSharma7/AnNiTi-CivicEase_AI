class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str):
        self.status, self.code, self.message = status, code, message


def ok(data=None) -> dict:
    return {"ok": True, "data": data, "error": None}
