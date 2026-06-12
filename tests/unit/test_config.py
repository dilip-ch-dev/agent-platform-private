import pytest
from pydantic import ValidationError

from app.config import Config, ModelParams


class TestModelParams:
    def test_accepts_valid_bounds(self) -> None:
        p = ModelParams(temperature=0.0, max_tokens=1)
        assert p.temperature == 0.0

    def test_rejects_negative_temperature(self) -> None:
        with pytest.raises(ValidationError):
            ModelParams(temperature=-0.1, max_tokens=100)

    def test_rejects_temperature_above_two(self) -> None:
        with pytest.raises(ValidationError):
            ModelParams(temperature=2.1, max_tokens=100)

    def test_rejects_zero_max_tokens(self) -> None:
        with pytest.raises(ValidationError):
            ModelParams(temperature=0.5, max_tokens=0)

    def test_strict_mode_rejects_string_temperature(self) -> None:
        with pytest.raises(ValidationError):
            ModelParams(temperature="0.5", max_tokens=100)


class TestConfig:
    def test_loads_from_environment(self) -> None:
        # conftest.py provides every required field via env vars
        cfg = Config()
        assert cfg.env == "test"
        assert cfg.injection_mode in ("flag_only", "block")

    def test_param_properties_are_bounded(self) -> None:
        cfg = Config()
        assert 0.0 <= cfg.reasoning_params.temperature <= 2.0
        assert cfg.reasoning_params.max_tokens >= 1

    def test_rejects_invalid_injection_mode(self, monkeypatch) -> None:
        monkeypatch.setenv("INJECTION_MODE", "yolo")
        with pytest.raises(ValidationError):
            Config()

    def test_rejects_invalid_llm_provider(self, monkeypatch) -> None:
        monkeypatch.setenv("LLM_PROVIDER", "openai")  # must be openai_compatible
        with pytest.raises(ValidationError):
            Config()
