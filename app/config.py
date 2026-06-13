import os
from pathlib import Path

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV = os.getenv("ENV", "development")
_env_file = f".env.{_ENV}" if Path(f".env.{_ENV}").exists() else ".env"


class ModelParams(BaseModel):
    model_config = ConfigDict(strict=True)

    temperature: float = Field(ge=0.0, le=2.0)
    max_tokens: int = Field(ge=1, le=8192)


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=_env_file, extra="ignore")

    # Environment
    env: str
    debug: bool

    # API keys — empty string allowed so CI runs without real keys
    anthropic_api_key: str = ""
    tavily_api_key: str = ""
    openai_api_key: str = ""

    # Models
    extraction_model: str
    reasoning_model: str
    extraction_temperature: float
    extraction_max_tokens: int
    reasoning_temperature: float
    reasoning_max_tokens: int

    # Pipeline thresholds
    retrieval_min_score: float
    top_k_retrieval: int
    confidence_threshold: float
    injection_threshold: float
    groundedness_threshold: float
    groundedness_model: str = ""

    # Storage
    chroma_path: str
    audit_log_path: str
    api_url: str

    # Observability (optional — needed with langfuse extra)
    langfuse_host: str = ""
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""

    @property
    def extraction_params(self) -> ModelParams:
        return ModelParams(
            temperature=self.extraction_temperature,
            max_tokens=self.extraction_max_tokens,
        )

    @property
    def reasoning_params(self) -> ModelParams:
        return ModelParams(
            temperature=self.reasoning_temperature,
            max_tokens=self.reasoning_max_tokens,
        )


cfg = Config()


class ModelRegistry:
    """Returns a LangChain chat model configured for the given task."""

    @staticmethod
    def get_model(task: str = "reasoning") -> BaseChatModel:
        from langchain_anthropic import ChatAnthropic

        params = cfg.extraction_params if task == "extraction" else cfg.reasoning_params
        model_id = cfg.extraction_model if task == "extraction" else cfg.reasoning_model

        return ChatAnthropic(
            model=model_id,
            temperature=params.temperature,
            max_tokens=params.max_tokens,
            anthropic_api_key=cfg.anthropic_api_key,
        )
