"""JSONL audit logger.

One line per event: ``{"ts": ..., "trace_id": ..., "event": ..., "payload": ...}``.

Privacy model (CLAUDE.md rule 6): the real guarantee is that callers redact
at the request boundary and only ever log ``redacted_*`` fields. This logger
adds a mechanical *backstop* — it rejects any payload carrying a known
raw-input key (``question`` / ``raw_question`` / ``original_question``) at
any nesting depth. The backstop catches the obvious mistake of logging a raw
key; it cannot catch raw PII smuggled under an innocent key name, which is
why redaction-at-the-boundary — not this check — is the actual protection.
"""

import json
import time
from pathlib import Path

_FORBIDDEN_PAYLOAD_KEYS = frozenset({"question", "raw_question", "original_question"})


def _find_forbidden_keys(obj: object) -> list[str]:
    """Return any forbidden raw-input keys found anywhere in a nested payload."""
    if isinstance(obj, dict):
        hit = _FORBIDDEN_PAYLOAD_KEYS & obj.keys()
        if hit:
            return sorted(hit)
        for value in obj.values():
            found = _find_forbidden_keys(value)
            if found:
                return found
    elif isinstance(obj, (list | tuple)):
        for item in obj:
            found = _find_forbidden_keys(item)
            if found:
                return found
    return []


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
        forbidden = _find_forbidden_keys(payload)
        if forbidden:
            raise ValueError(
                f"Audit payload must never contain raw input keys {forbidden} "
                "(found at any nesting depth); redact first and pass 'redacted_question'."
            )

        record = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "trace_id": trace_id,
            "event": event,
            "payload": payload,
        }
        with self._path().open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
