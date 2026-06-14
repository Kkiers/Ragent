from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass(frozen=True)
class TestSettings:
    data: Dict[str, Any]

    @classmethod
    def load(cls) -> "TestSettings":
        root = Path(__file__).resolve().parents[1]
        path = root / "config" / "test_settings.json"
        raw = path.read_text(encoding="utf-8")
        return cls(data=json.loads(raw))

    def get(self, *keys: str, default: Any = None) -> Any:
        cur: Any = self.data
        for k in keys:
            if not isinstance(cur, dict) or k not in cur:
                return default
            cur = cur[k]
        return cur


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]

