"""JSONL audit logger.

One line per event: ``{"ts": ..., "trace_id": ..., "event": ..., "payload": ...}``.

CLAUDE.md rule 6 is enforced mechanically here: a payload containing a raw
``question`` key is rejected — callers must redact first and pass
``redacted_question``.
"""

import json
import time
from pathlib import Path

_FORBIDDEN_PAYLOAD_KEYS = frozenset({"question", "raw_question", "original_question"})


class AuditLogger:
    """Append-only JSONL audit log. One file per day: ``audit-YYYY-MM-DD.jsonl``."""

    def __init__(self, log_dir: str) -> None:
        self._dir = Path(log_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self) -> Path:
        day = time.strftime("%Y-%m-%d", time.gmtime())
        return self._dir / f"audit-{day}.jsonl"

    def log_event(
        self,
        trace_id: str,
        event: str,
        payload: dict[str, object] | None = None,
    ) -> None:
        payload = payload or {}
        forbidden = _FORBIDDEN_PAYLOAD_KEYS & payload.keys()
        if forbidden:
            raise ValueError(
                f"Audit payload must never contain raw input keys {sorted(forbidden)}; "
                "redact first and pass 'redacted_question'."
            )

        record = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "trace_id": trace_id,
            "event": event,
            "payload": payload,
        }
        with self._path().open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
