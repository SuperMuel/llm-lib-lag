from pydantic import BaseModel, HttpUrl, Field
from datetime import date, datetime, UTC
from typing import Optional, Literal


def utc_factory() -> datetime:
    return datetime.now(UTC)


class TechVersionGroundTruth(BaseModel):
    """
    Represents the ground truth version information for a piece of software.
    """

    software_name: str = Field(
        ...,
        description="The name of the software (e.g., 'Python', 'Django', 'requests')",
        min_length=1,
    )

    version: str = Field(
        ..., description="The version string (e.g., '3.12.1', '5.0.2', '2.31.0')"
    )

    release_date: date | None = Field(
        default=None, description="The official release date of the version"
    )

    url: HttpUrl | None = Field(
        default=None, description="The URL where the version information was obtained"
    )

    timestamp: datetime = Field(
        default_factory=utc_factory,
        description="The date and time when the data was collected",
    )


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class LLMConfig(BaseModel):
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

    ground_truth: TechVersionGroundTruth

    llm_config: LLMConfig

    timestamp: datetime = Field(default_factory=utc_factory)

    # prompt_template: str = Field(
    #     ..., description="Template used for generating the prompt"
    # )
    # messages: list[Message] = Field(
    #     ..., description="List of messages in the conversation"
    # )

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
