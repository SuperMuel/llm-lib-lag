from datetime import date

from pydantic import HttpUrl
from .models import SoftwareVersionGroundTruth

GROUND_TRUTHS = [
    SoftwareVersionGroundTruth(
        software_name="Python",
        version="3.13.1",
        release_date=date(2024, 12, 3),
        url=HttpUrl("https://www.python.org/downloads/release/python-3131/"),
    ),
    SoftwareVersionGroundTruth(
        software_name="FastAPI",
        version="0.115.8",
        # release_date=date(2024, 12, 3),
        url=HttpUrl("https://pypi.org/pypi/fastapi/json"),
    ),
]
