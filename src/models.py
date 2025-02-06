from pydantic import BaseModel, HttpUrl, Field
from datetime import date, datetime, UTC
from typing import Optional


def utc_factory() -> datetime:
    return datetime.now(UTC)


class SoftwareVersionGroundTruth(BaseModel):
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

    url: HttpUrl = Field(
        ..., description="The URL where the version information was obtained"
    )

    timestamp: datetime = Field(
        default_factory=utc_factory,
        description="The date and time when the data was collected",
    )
