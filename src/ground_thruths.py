from datetime import date
from .models import SoftwareVersionGroundTruth

GROUND_TRUTHS = [
    SoftwareVersionGroundTruth(
        software_name="Python",
        version="3.13.1",
        release_date=date(2024, 12, 3),
    )
]
