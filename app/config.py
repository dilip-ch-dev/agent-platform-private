"""Single source of truth for all settings.

Rules (see CLAUDE.md):
- This is the ONLY module that reads environment / .env files.
- Everywhere else: ``from app.config import cfg``.
- Every tunable lives in .env and is exposed as a typed field here.
"""

import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Production must never silently fall back to the development .env:
#   production + .env.production present  -> load it
#   production + .env.production missing  -> load NO file; real env vars only
#   any other ENV                         -> load .env
_ENV = os.getenv("ENV", "development")
if _ENV == "production":
    _prod_env = Path(".env.production")
    _env_file: str | None = ".env.production" if _prod_env.exists() else None
else:
    _env_file = ".env"


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
    openai_api_key: str = ""
    tavily_api_key: str = ""
    featherless_api_key: str = ""

    # LLM provider selection (provider-agnostic; flip via env, never via code)
    # "anthropic"          -> langchain-anthropic
    # "openai_compatible"  -> langchain-openai with a custom base_url
    #                         (Featherless, event-credit providers, local servers)
    llm_provider: Literal["anthropic", "openai_compatible"] = "anthropic"
    openai_compatible_base_url: str = "https://api.featherless.ai/v1"

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

    # Guardrail modes
    # flag_only: score and record, never block (use while tuning thresholds)
    # block:     refuse the request when score >= injection_threshold
    injection_mode: Literal["flag_only", "block"] = "block"

    # Prompting
    system_prompt: str = ""

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
    """Returns a LangChain chat model configured for the given task.

    Provider-agnostic by design: the provider is chosen by ``LLM_PROVIDER``
    in .env, so switching to event-credit providers (e.g. Featherless via
    its OpenAI-compatible endpoint) is an env flip, not a code change.

    LangChain imports are deliberately lazy so that importing app.config
    never pulls heavy dependencies.
    """

    @staticmethod
    def get_model(task: str = "reasoning"):
        params = cfg.extraction_params if task == "extraction" else cfg.reasoning_params
        model_id = cfg.extraction_model if task == "extraction" else cfg.reasoning_model

        if cfg.llm_provider == "openai_compatible":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=model_id,
                temperature=params.temperature,
                max_tokens=params.max_tokens,
                base_url=cfg.openai_compatible_base_url,
                api_key=cfg.featherless_api_key or cfg.openai_api_key,
            )

        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=model_id,
            temperature=params.temperature,
            max_tokens=params.max_tokens,
            anthropic_api_key=cfg.anthropic_api_key,
        )
