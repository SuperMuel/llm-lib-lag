from enum import Enum
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime, UTC


def utc_factory() -> datetime:
    return datetime.now(UTC)


class PackageManager(str, Enum):
    NPM = "npm"
    MAVEN = "maven"
    RUBYGEMS = "rubygems"
    PYPI = "pypi"
    CARGO = "cargo"


class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    RUBY = "ruby"
    JAVA = "java"
    C_SHARP = "csharp"
    GO = "go"
    RUST = "rust"

    @property
    def name(self) -> str:
        return self.value


class LibraryIdentifier(BaseModel):
    model_config = ConfigDict(frozen=True)

    package_manager: PackageManager
    name: str = Field(..., examples=["react", "fastapi"])


class TechVersionGroundTruth(BaseModel):
    """
    Represents the ground truth version information for a piece of software.
    """

    model_config = ConfigDict(frozen=True)

    tech: LibraryIdentifier | Language

    version: str = Field(..., examples=["3.12.1", "19.0.0"])

    release_date: date | None = Field(
        default=None, description="The official release date of the version"
    )


class LLMConfig(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",  # Prevents extra attributes
    )

    provider: Literal[
        "anthropic",
        "openai",
        "google_genai",
        "mistralai",
        "fireworks",
        "perplexity",
        "groq",
    ] = Field(
        ...,
        description="LLM provider (e.g., 'anthropic', 'openai')",
    )
    model: str = Field(
        ...,
        description="Model name/version used",
        examples=[
            "gpt-4o-mini",
            "gemini-1.5-flash",
            "mistral-small-2501",
            "accounts/fireworks/models/deepseek-v3",
            "deepseek-r1-distill-qwen-32b",
        ],
    )

    def __hash__(self) -> int:
        return hash((self.provider, self.model))


class EvaluationRun(BaseModel):
    """Represents a single evaluation run of an LLM model on a specific library/framework."""

    model_config = ConfigDict(frozen=True)

    ground_truth: TechVersionGroundTruth

    llm_config: LLMConfig

    timestamp: datetime = Field(default_factory=utc_factory)

    # Results
    execution_time_seconds: float = Field(
        ..., description="Time taken for the evaluation in seconds"
    )

    output: str = Field(
        ...,
        description="Output of the evaluation",
        examples=["The latest stable version of Python is **3.12.1**"],
    )

    parsed_version: str | None = Field(
        None,
        description="Parsed version from the output",
        examples=["3.12.1"],
    )

    parsed_version_exists: bool | None = Field(
        default=None,
        description="If we could verify that the parsed version exists in the package manager registry",
    )

    lag_days: int | None = Field(
        default=None,
        description="Lag in days between the release date of the ground truth and the release date of the parsed version",
    )

    # tokens_used: int | None = Field(
    #     None, description="Number of tokens used in the conversation"
    # )
