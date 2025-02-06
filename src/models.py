from pydantic import BaseModel, HttpUrl, Field
from datetime import date, datetime
from typing import Optional


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
        None, description="The official release date of the version"
    )
    source_url: HttpUrl = Field(
        ..., description="The URL where the version information was obtained"
    )
    timestamp: datetime = Field(
        ..., description="The date and time when the data was collected"
    )
