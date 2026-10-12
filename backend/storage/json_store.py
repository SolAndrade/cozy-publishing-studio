import json
from pathlib import Path


class JsonProjectStore:
    """Local/dev persistence. Production will swap this for a private database."""

    def __init__(self, root: str | Path = ".cozy-data") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save_raw(self, project_id: str, payload: dict) -> Path:
        target = self.root / f"{project_id}.json"
        temp = target.with_suffix(".tmp")
        temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(target)
        return target

    def load_raw(self, project_id: str) -> dict:
        return json.loads((self.root / f"{project_id}.json").read_text(encoding="utf-8"))
