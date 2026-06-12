import json

import pytest

from app.audit import AuditLogger


class TestAuditLogger:
    def test_writes_parseable_jsonl(self, tmp_path) -> None:
        logger = AuditLogger(str(tmp_path))
        logger.log_event("trace-1", "ask_received", {"redacted_question": "hi"})
        logger.log_event("trace-1", "ask_answered", {"status": "answered"})

        files = list(tmp_path.glob("audit-*.jsonl"))
        assert len(files) == 1
        lines = files[0].read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        first = json.loads(lines[0])
        assert first["trace_id"] == "trace-1"
        assert first["event"] == "ask_received"
        assert "ts" in first

    def test_creates_directory(self, tmp_path) -> None:
        target = tmp_path / "nested" / "audit"
        AuditLogger(str(target))
        assert target.is_dir()

    def test_rejects_raw_question_key(self, tmp_path) -> None:
        logger = AuditLogger(str(tmp_path))
        with pytest.raises(ValueError, match="redact"):
            logger.log_event("t", "ask_received", {"question": "raw PII here"})

    def test_rejects_raw_question_aliases(self, tmp_path) -> None:
        logger = AuditLogger(str(tmp_path))
        with pytest.raises(ValueError):
            logger.log_event("t", "e", {"raw_question": "x"})

    def test_empty_payload_ok(self, tmp_path) -> None:
        logger = AuditLogger(str(tmp_path))
        logger.log_event("t", "startup")
        files = list(tmp_path.glob("audit-*.jsonl"))
        assert json.loads(files[0].read_text())["payload"] == {}
