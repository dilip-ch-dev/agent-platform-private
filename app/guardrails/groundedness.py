"""Groundedness (faithfulness) guardrail.

``verify(claim, evidence)`` returns an NLI-style label:
``"entailment" | "neutral" | "contradiction"``.

Default verifier is lexical (zero heavy deps, CPU-instant, hackathon-safe).
If the ``pipeline`` extra is installed (transformers + torch), pass
``use_nli=True`` to use ``cross-encoder/nli-deberta-v3-base`` instead.

``external_verify(claim, api_key)`` checks a claim against Tavily search.
All functions are pure / side-effect free apart from the explicit HTTP call.
"""

import re

import httpx

_WORD = re.compile(r"[a-z0-9]+")
_NEGATORS = frozenset({"not", "no", "never", "none", "cannot", "n't", "without"})
_STOPWORDS = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "of", "in", "on", "at", "to", "for", "from", "with", "by", "as",
    "and", "or", "but", "if", "then", "it", "its", "this", "that",
    "these", "those", "he", "she", "they", "we", "you", "i",
})

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")

_TAVILY_URL = "https://api.tavily.com/search"


def split_claims(text: str) -> list[str]:
    """Split an answer into atomic claims (sentences) for per-claim verification."""
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text)]
    return [s for s in sentences if len(s.split()) >= 3]


def _content_tokens(text: str) -> set[str]:
    return {t for t in _WORD.findall(text.lower()) if t not in _STOPWORDS}


def _has_negation(text: str) -> bool:
    lowered = text.lower()
    return any(n in lowered.split() or n in lowered for n in _NEGATORS)


def verify(claim: str, evidence: str, use_nli: bool = False) -> str:
    """Label whether ``evidence`` supports ``claim``.

    Lexical default: token-overlap containment of the claim in the evidence.
    High overlap + matching polarity -> entailment; high overlap + opposite
    polarity -> contradiction; otherwise neutral. Deliberately conservative:
    when unsure, return neutral and let the gate abstain.
    """
    if use_nli:
        label = _nli_verify(claim, evidence)
        if label is not None:
            return label

    claim_tokens = _content_tokens(claim)
    if not claim_tokens:
        return "neutral"

    evidence_tokens = _content_tokens(evidence)
    overlap = len(claim_tokens & evidence_tokens) / len(claim_tokens)

    if overlap >= 0.6:
        if _has_negation(claim) != _has_negation(evidence):
            return "contradiction"
        return "entailment"
    return "neutral"


def _nli_verify(claim: str, evidence: str) -> str | None:
    """NLI cross-encoder verification. Returns None if deps are missing."""
    try:
        from sentence_transformers import CrossEncoder
    except ImportError:
        return None

    model = _get_nli_model(CrossEncoder)
    scores = model.predict([(evidence, claim)])[0]
    # nli-deberta-v3-base label order: contradiction, entailment, neutral
    labels = ["contradiction", "entailment", "neutral"]
    return labels[int(scores.argmax())]


_nli_model_cache: dict[str, object] = {}


def _get_nli_model(cross_encoder_cls):
    if "model" not in _nli_model_cache:
        _nli_model_cache["model"] = cross_encoder_cls("cross-encoder/nli-deberta-v3-base")
    return _nli_model_cache["model"]


def external_verify(
    claim: str,
    api_key: str,
    timeout: float = 10.0,
) -> tuple[bool, str | None]:
    """Verify a claim against Tavily web search.

    Returns ``(confirmed, source_url)``. Without an API key, or on any
    network error, returns ``(False, None)`` — external verification is a
    bonus signal, never a hard dependency.
    """
    if not api_key:
        return False, None

    try:
        response = httpx.post(
            _TAVILY_URL,
            json={"api_key": api_key, "query": claim, "max_results": 3},
            timeout=timeout,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
    except (httpx.HTTPError, ValueError):
        return False, None

    for result in results:
        content = result.get("content", "")
        if verify(claim, content) == "entailment":
            return True, result.get("url")
    return False, None
