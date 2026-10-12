from backend.domain.states import QAResult


ALLOWED={x.value for x in QAResult}


def normalize_review(payload: dict) -> dict:
    result=str(payload.get("result","")).upper()
    if result not in ALLOWED:
        raise ValueError("Reviewer must return PASS, FIX_LOCAL, or REGENERATE")
    reason=str(payload.get("reason","")).strip()
    if result!="PASS" and not reason:
        raise ValueError("A failed review requires a concrete material reason")
    return {"result":result,"reason":reason}
