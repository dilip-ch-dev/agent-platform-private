"""Test bootstrap.

Sets every required config field as an environment variable BEFORE any
``app.*`` import, so the test suite runs with or without a local .env file
(pydantic-settings gives real environment variables precedence over .env).
"""

import os
import tempfile

_TEST_ENV = {
    "ENV": "test",
    "DEBUG": "true",
    "EXTRACTION_MODEL": "claude-haiku-4-5",
    "REASONING_MODEL": "claude-sonnet-4-5",
    "EXTRACTION_TEMPERATURE": "0.0",
    "EXTRACTION_MAX_TOKENS": "1000",
    "REASONING_TEMPERATURE": "0.0",
    "REASONING_MAX_TOKENS": "2000",
    "RETRIEVAL_MIN_SCORE": "0.35",
    "TOP_K_RETRIEVAL": "3",
    "CONFIDENCE_THRESHOLD": "0.7",
    "INJECTION_THRESHOLD": "0.75",
    "GROUNDEDNESS_THRESHOLD": "0.6",
    "INJECTION_MODE": "block",
    "CHROMA_PATH": tempfile.mkdtemp(prefix="bt-test-chroma-"),
    "AUDIT_LOG_PATH": tempfile.mkdtemp(prefix="bt-test-audit-"),
    "API_URL": "http://127.0.0.1:8000",
}

for _key, _value in _TEST_ENV.items():
    os.environ.setdefault(_key, _value)
