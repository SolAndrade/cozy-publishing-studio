import hmac
import os


def api_auth_required() -> bool:
    return os.getenv("COZY_ENV","development").strip().lower()=="production"


def api_token_configured() -> bool:
    return bool(os.getenv("COZY_API_TOKEN","").strip())


def authorize_header(value: str | None) -> bool:
    if not api_auth_required():
        return True
    expected=os.getenv("COZY_API_TOKEN","").strip()
    if not expected or not value or not value.startswith("Bearer "):
        return False
    supplied=value.removeprefix("Bearer ").strip()
    return hmac.compare_digest(supplied,expected)
