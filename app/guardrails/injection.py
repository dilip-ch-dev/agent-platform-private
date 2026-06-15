"""Prompt-injection scoring and blocking policy."""

import re

_SIGNALS: list[tuple[float, re.Pattern[str]]] = [
    (
        0.95,
        re.compile(
            r"ignore\s+(all\s+|any\s+)?(previous|prior|above|earlier)\s+"
            r"(instructions?|prompts?|rules?)",
            re.I,
        ),
    ),
    (
        0.95,
        re.compile(
            r"disregard\s+(all\s+|any\s+)?(previous|prior|above|earlier|your)\s+"
            r"((previous|prior|above|earlier)\s+)?(instructions?|prompts?|rules?|guidelines?)",
            re.I,
        ),
    ),
    (
        0.90,
        re.compile(
            r"(reveal|show|print|repeat|output|leak)\b.{0,40}\b"
            r"(system\s+prompt|hidden\s+instructions?|initial\s+prompt)",
            re.I,
        ),
    ),
    (
        0.90,
        re.compile(
            r"\byou\s+are\s+now\b.{0,60}\b"
            r"(DAN|jailbroken|unrestricted|without\s+(any\s+)?(rules|restrictions|filters))",
            re.I,
        ),
    ),
    (0.85, re.compile(r"\bdo\s+anything\s+now\b|\bDAN\s+mode\b", re.I)),
    (
        0.80,
        re.compile(
            r"\b(developer|debug|god|admin)\s+mode\b.{0,40}\b(enabled?|activated?|on)\b",
            re.I,
        ),
    ),
    (
        0.80,
        re.compile(
            r"\bpretend\s+(that\s+)?you\s+(are|have)\b.{0,60}\b"
            r"(no\s+(rules|restrictions|guidelines)|evil|unfiltered)",
            re.I,
        ),
    ),
    (0.75, re.compile(r"^\s*#{1,4}\s*(system|assistant)\s*:?\s*$", re.I | re.M)),
    (0.75, re.compile(r"<\|?(system|im_start|endoftext)\|?>", re.I)),
    (0.70, re.compile(r"\bnew\s+instructions?\s*:", re.I)),
    (
        0.70,
        re.compile(
            r"\boverride\b.{0,30}\b(safety|guardrails?|filters?|instructions?)", re.I
        ),
    ),
    (0.60, re.compile(r"\b[A-Za-z0-9+/]{120,}={0,2}\b")),
    (
        0.50,
        re.compile(
            r"\brespond\s+only\s+with\b.{0,40}\b(json|code|yes)\b.{0,40}"
            r"\bno\s+matter\s+what\b",
            re.I,
        ),
    ),
]


def score(text: str) -> tuple[float, list[str]]:
    """Return the strongest injection score and matching snippets."""
    max_score = 0.0
    flagged: list[str] = []
    for weight, pattern in _SIGNALS:
        match = pattern.search(text)
        if match:
            flagged.append(match.group(0)[:120])
            max_score = max(max_score, weight)
    return max_score, flagged


def is_blocked(injection_score: float, threshold: float, mode: str) -> bool:
    if mode == "flag_only":
        return False
    if mode == "block":
        return injection_score >= threshold
    return True
