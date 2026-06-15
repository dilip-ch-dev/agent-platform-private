"""PII redaction helpers."""

import re

_IP_OCTET = r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"

_PATTERNS: dict[str, re.Pattern[str]] = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,19}\b"),
    "ip_address": re.compile(
        rf"\b{_IP_OCTET}\.{_IP_OCTET}\.{_IP_OCTET}\.{_IP_OCTET}\b"
    ),
    "phone": re.compile(
        r"(?<![\d-])(?:\+?1[ .-]?)?(?:\(\d{3}\)|\d{3})[ .-]\d{3}[ .-]\d{4}(?![\d-])"
    ),
    "api_key": re.compile(r"\b(?:sk|pk|rk)-[A-Za-z0-9_-]{16,}\b|\bAKIA[0-9A-Z]{16}\b"),
}


def _luhn_valid(value: str) -> bool:
    digits = [int(char) for char in value if char.isdigit()]
    if not 13 <= len(digits) <= 19:
        return False

    checksum = 0
    for index, digit in enumerate(reversed(digits)):
        if index % 2:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


def redact(
    text: str,
    extra_patterns: dict[str, str] | None = None,
) -> tuple[str, list[str]]:
    """Return redacted text and sorted unique PII type names."""
    found: set[str] = set()
    redacted = text

    patterns: list[tuple[str, re.Pattern[str]]] = list(_PATTERNS.items())
    if extra_patterns:
        patterns.extend(
            (name, re.compile(pattern)) for name, pattern in extra_patterns.items()
        )

    for pii_type, pattern in patterns:

        def replace(match: re.Match[str], current_type: str = pii_type) -> str:
            value = match.group(0)
            if current_type == "credit_card" and not _luhn_valid(value):
                return value
            found.add(current_type)
            return f"[REDACTED:{current_type.upper()}]"

        redacted = pattern.sub(replace, redacted)

    return redacted, sorted(found)
