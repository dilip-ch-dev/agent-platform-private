from app.guardrails.pii import _luhn_valid, redact


def test_redacts_email() -> None:
    redacted, types = redact("Contact me at jane.doe@example.com please")
    assert "jane.doe@example.com" not in redacted
    assert "[REDACTED:EMAIL]" in redacted
    assert types == ["email"]


def test_redacts_ssn() -> None:
    redacted, types = redact("My SSN is 123-45-6789.")
    assert "123-45-6789" not in redacted
    assert "ssn" in types


def test_redacts_phone() -> None:
    redacted, types = redact("Call me on 415-555-2671 tomorrow")
    assert "415-555-2671" not in redacted
    assert "phone" in types


def test_redacts_luhn_valid_credit_card() -> None:
    redacted, types = redact("Card: 4111 1111 1111 1111")
    assert "credit_card" in types
    assert "4111" not in redacted


def test_redacts_ip_address() -> None:
    _, types = redact("Server at 192.168.1.100 is down")
    assert "ip_address" in types


def test_redacts_api_key() -> None:
    redacted, types = redact("Use key sk-abcdefghij1234567890XY")
    assert "api_key" in types
    assert "sk-abcdefghij" not in redacted


def test_reports_multiple_types_sorted() -> None:
    _, types = redact("Email a@b.co, SSN 123-45-6789")
    assert types == sorted(types)
    assert {"email", "ssn"} <= set(types)


def test_extra_domain_pattern() -> None:
    redacted, types = redact(
        "Reference CASE-123456 for details",
        extra_patterns={"case_id": r"CASE-\d{6}"},
    )
    assert "case_id" in types
    assert "CASE-123456" not in redacted


def test_clean_text_untouched() -> None:
    text = "What is the refund policy for enterprise customers?"
    redacted, types = redact(text)
    assert redacted == text
    assert types == []


def test_luhn_rejects_random_digits() -> None:
    redacted, types = redact("Order number 1234 5678 9012 3457 shipped")
    assert "credit_card" not in types
    assert "1234 5678 9012 3457" in redacted


def test_version_numbers_are_not_phone_numbers() -> None:
    _, types = redact("Upgrade to version 3.11 today")
    assert "phone" not in types


def test_luhn_validity() -> None:
    assert _luhn_valid("4111111111111111")
    assert not _luhn_valid("4111111111111112")
    assert not _luhn_valid("411111")
