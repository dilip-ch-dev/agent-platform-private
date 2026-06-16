import pytest
from pydantic import ValidationError

from app.config import Config, ModelParams, cfg


class TestModelParams:
    def test_accepts_valid_params(self) -> None:
        params = ModelParams(temperature=0.5, max_tokens=1000)
        assert params.temperature == 0.5
        assert params.max_tokens == 1000

    def test_rejects_temperature_above_max(self) -> None:
        with pytest.raises(ValidationError):
            ModelParams(temperature=3.0, max_tokens=1000)

    def test_rejects_temperature_below_min(self) -> None:
        with pytest.raises(ValidationError):
            ModelParams(temperature=-0.1, max_tokens=1000)

    def test_rejects_zero_max_tokens(self) -> None:
        with pytest.raises(ValidationError):
            ModelParams(temperature=0.5, max_tokens=0)


class TestConfig:
    def test_cfg_loads(self) -> None:
        assert cfg.env == "development"

    def test_cfg_has_thresholds(self) -> None:
        assert 0.0 < cfg.retrieval_min_score < 1.0
        assert 0.0 < cfg.confidence_threshold < 1.0
        assert 0.0 < cfg.injection_threshold < 1.0
        assert 0.0 < cfg.groundedness_threshold < 1.0
        assert cfg.injection_mode in ("flag_only", "block")

    def test_cfg_top_k_positive(self) -> None:
        assert cfg.top_k_retrieval > 0

    def test_extraction_params_property(self) -> None:
        params = cfg.extraction_params
        assert isinstance(params, ModelParams)
        assert 0.0 <= params.temperature <= 2.0
        assert params.max_tokens >= 1

    def test_reasoning_params_property(self) -> None:
        params = cfg.reasoning_params
        assert isinstance(params, ModelParams)
        assert 0.0 <= params.temperature <= 2.0
        assert params.max_tokens >= 1

    def test_extraction_model_set(self) -> None:
        assert cfg.extraction_model != ""

    def test_reasoning_model_set(self) -> None:
        assert cfg.reasoning_model != ""

    def test_rejects_invalid_injection_mode(self, monkeypatch) -> None:
        monkeypatch.setenv("INJECTION_MODE", "typo")
        with pytest.raises(ValidationError):
            Config()

    @pytest.mark.parametrize("threshold", ["-0.1", "1.1"])
    def test_rejects_invalid_injection_threshold(self, monkeypatch, threshold) -> None:
        monkeypatch.setenv("INJECTION_THRESHOLD", threshold)
        with pytest.raises(ValidationError):
            Config()
