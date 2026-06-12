"""PII redaction guardrail.

``redact(text)`` is a pure function: no config reads, no side effects.
Callers (pipeline nodes) pass any domain-specific extra patterns in.

Applied inbound (question) and outbound (answer). The audit log must only
ever receive the redacted text — never the original (CLAUDE.md rule 6).
"""

import re

# Order matters: more specific patterns first so e.g. an SSN inside a
# longer digit string is not half-eaten by the phone pattern.
_PATTERNS: dict[str, re.Pattern[str]] = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,19}\b"),
    "ip_address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "phone": re.compile(
        r"(?<![\d-])(?:\+?\d{1,3}[ .-]?)?(?:\(\d{2,4}\)[ .-]?)?\d{3}[ .-]\d{3,4}[ .-]?\d{0,4}(?![\d-])"
    ),
    "api_key": re.compile(r"\b(?:sk|pk|rk)-[A-Za-z0-9_-]{16,}\b|\bAKIA[0-9A-Z]{16}\b"),
}


def _luhn_valid(digits: str) -> bool:
    """Luhn checksum — rejects random digit runs that merely look like cards."""
    ds = [int(c) for c in digits if c.isdigit()]
    if not 13 <= len(ds) <= 19:
        return False
    checksum = 0
    for i, d in enumerate(reversed(ds)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


def redact(
    text: str,
    extra_patterns: dict[str, str] | None = None,
) -> tuple[str, list[str]]:
    """Replace PII spans with ``[REDACTED:TYPE]`` tokens.

    Returns ``(redacted_text, sorted list of unique PII types found)``.
    ``extra_patterns`` lets a skin add domain types (e.g. case numbers)
    without editing this module: ``{"case_id": r"CASE-\\d{6}"}``.
    """
    found: set[str] = set()
    redacted = text

    patterns: list[tuple[str, re.Pattern[str]]] = list(_PATTERNS.items())
    if extra_patterns:
        patterns += [(name, re.compile(p)) for name, p in extra_patterns.items()]

    for pii_type, pattern in patterns:

        def _sub(match: re.Match[str], _t: str = pii_type) -> str:
            value = match.group(0)
            # credit_card needs a checksum pass to avoid false positives
            if _t == "credit_card" and not _luhn_valid(value):
                return value
            found.add(_t)
            return f"[REDACTED:{_t.upper()}]"

        redacted = pattern.sub(_sub, redacted)

    return redacted, sorted(found)
