from datetime import date

from pydantic import HttpUrl
from .models import TechVersionGroundTruth

GROUND_TRUTHS = [
    TechVersionGroundTruth(
        tech_name="Python",
        version="3.13.1",
        release_date=date(2024, 12, 3),
        url=HttpUrl("https://www.python.org/downloads/release/python-3131/"),
    ),
    TechVersionGroundTruth(
        tech_name="FastAPI",
        version="0.115.8",
        # release_date=date(2024, 12, 3),
        url=HttpUrl("https://pypi.org/pypi/fastapi/json"),
    ),
    # django
    TechVersionGroundTruth(
        tech_name="Django",
        version="5.1.6",
        # release_date=date(2024, 12, 3),
    ),
    TechVersionGroundTruth(
        tech_name="SQLAlchemy",
        version="2.0.37",
        # release_date=date(2024, 12, 3),
    ),
    # Pydantic
    TechVersionGroundTruth(
        tech_name="pydantic",
        version="2.10.6",
        # release_date=date(2024, 12, 3),
    ),
]
