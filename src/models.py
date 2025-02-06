from enum import Enum
from pydantic import BaseModel, ConfigDict, HttpUrl, Field
from datetime import date, datetime, UTC
from typing import Optional, Literal


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
    model_config = ConfigDict(frozen=True)

    provider: str = Field(
        ...,
        description="LLM provider (e.g., 'anthropic', 'openai')",
        examples=["anthropic", "openai", "google", "mistralai", "fireworks"],
    )
    model: str = Field(
        ...,
        description="Model name/version used",
        examples=[
            "gpt-4o-mini",
            "gemini-1.5-flash",
            "mistral-small-2501",
            "accounts/fireworks/models/deepseek-v3",
        ],
    )


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

    # tokens_used: int | None = Field(
    #     None, description="Number of tokens used in the conversation"
    # )
