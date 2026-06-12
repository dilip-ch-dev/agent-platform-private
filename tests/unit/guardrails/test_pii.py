from app.guardrails.pii import _luhn_valid, redact


class TestRedactDetects:
    def test_email(self) -> None:
        redacted, types = redact("Contact me at jane.doe@example.com please")
        assert "jane.doe@example.com" not in redacted
        assert "[REDACTED:EMAIL]" in redacted
        assert types == ["email"]

    def test_ssn(self) -> None:
        redacted, types = redact("My SSN is 123-45-6789.")
        assert "123-45-6789" not in redacted
        assert "ssn" in types

    def test_phone(self) -> None:
        redacted, types = redact("Call me on 415-555-2671 tomorrow")
        assert "415-555-2671" not in redacted
        assert "phone" in types

    def test_valid_credit_card(self) -> None:
        # 4111111111111111 is the canonical Luhn-valid Visa test number
        redacted, types = redact("Card: 4111 1111 1111 1111")
        assert "credit_card" in types
        assert "4111" not in redacted

    def test_ip_address(self) -> None:
        _, types = redact("Server at 192.168.1.100 is down")
        assert "ip_address" in types

    def test_api_key(self) -> None:
        redacted, types = redact("Use key sk-abcdefghij1234567890XY")
        assert "api_key" in types
        assert "sk-abcdefghij" not in redacted

    def test_multiple_types_sorted(self) -> None:
        _, types = redact("Email a@b.co, SSN 123-45-6789")
        assert types == sorted(types)
        assert {"email", "ssn"} <= set(types)

    def test_extra_domain_pattern(self) -> None:
        redacted, types = redact(
            "Reference CASE-123456 for details",
            extra_patterns={"case_id": r"CASE-\d{6}"},
        )
        assert "case_id" in types
        assert "CASE-123456" not in redacted


class TestRedactDoesNotOverfire:
    def test_clean_text_untouched(self) -> None:
        text = "What is the refund policy for enterprise customers?"
        redacted, types = redact(text)
        assert redacted == text
        assert types == []

    def test_luhn_rejects_random_digits(self) -> None:
        # 16 digits failing the Luhn checksum must NOT be flagged as a card
        redacted, types = redact("Order number 1234 5678 9012 3457 shipped")
        assert "credit_card" not in types

    def test_version_numbers_not_phone(self) -> None:
        _, types = redact("Upgrade to version 3.11 today")
        assert "phone" not in types


class TestLuhn:
    def test_valid(self) -> None:
        assert _luhn_valid("4111111111111111")

    def test_invalid(self) -> None:
        assert not _luhn_valid("4111111111111112")

    def test_too_short(self) -> None:
        assert not _luhn_valid("411111")
