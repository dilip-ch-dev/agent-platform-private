from app.guardrails.groundedness import external_verify, split_claims, verify


class TestSplitClaims:
    def test_splits_sentences(self) -> None:
        claims = split_claims("Revenue grew 12% in Q3. Churn dropped to 2.1%. Margins held steady.")
        assert len(claims) == 3

    def test_drops_fragments(self) -> None:
        claims = split_claims("Revenue grew strongly this quarter. Yes. OK.")
        assert claims == ["Revenue grew strongly this quarter."]

    def test_empty_text(self) -> None:
        assert split_claims("") == []


class TestVerify:
    def test_entailment_on_supported_claim(self) -> None:
        evidence = "The refund policy allows enterprise customers refunds within 30 days."
        claim = "Enterprise customers can request refunds within 30 days."
        assert verify(claim, evidence) == "entailment"

    def test_neutral_on_unrelated_evidence(self) -> None:
        evidence = "The cafeteria menu changes every Monday morning."
        claim = "Enterprise customers can request refunds within 30 days."
        assert verify(claim, evidence) == "neutral"

    def test_contradiction_on_negation_mismatch(self) -> None:
        evidence = "Enterprise customers cannot request refunds within 30 days, no exceptions."
        claim = "Enterprise customers can request refunds within 30 days."
        assert verify(claim, evidence) == "contradiction"

    def test_ordinary_word_containing_no_is_not_negation(self) -> None:
        # Regression: "innovation"/"technology" contain the substring "no"
        # but are not negations. A substring check used to flip these to
        # "contradiction"; word-boundary matching must read them as support.
        evidence = "The company reported innovation growth."
        claim = "The company reported growth."
        assert verify(claim, evidence) == "entailment"

    def test_contraction_still_counts_as_negation(self) -> None:
        evidence = "Enterprise customers can't request refunds within 30 days."
        claim = "Enterprise customers can request refunds within 30 days."
        assert verify(claim, evidence) == "contradiction"

    def test_empty_claim_is_neutral(self) -> None:
        assert verify("", "Some evidence text here.") == "neutral"

    def test_conservative_default(self) -> None:
        # Partial overlap below threshold must abstain (neutral), not guess
        evidence = "Refunds exist."
        claim = "Enterprise customers can request refunds within 30 days via the portal."
        assert verify(claim, evidence) == "neutral"


class TestExternalVerify:
    def test_no_api_key_returns_unconfirmed(self) -> None:
        confirmed, url = external_verify("The sky is blue.", api_key="")
        assert confirmed is False
        assert url is None

    def test_network_error_returns_unconfirmed(self, monkeypatch) -> None:
        import httpx

        def _boom(*args: object, **kwargs: object) -> object:
            raise httpx.ConnectError("no network")

        monkeypatch.setattr(httpx, "post", _boom)
        confirmed, url = external_verify("Any claim.", api_key="tvly-test")
        assert confirmed is False
        assert url is None
