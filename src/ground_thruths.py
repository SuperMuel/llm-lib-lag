from datetime import date
from .models import Language, TechVersionGroundTruth, LibraryIdentifier, PackageManager


GROUND_TRUTHS = [
    TechVersionGroundTruth(
        tech=Language.PYTHON,
        version="3.13.1",
        release_date=date(2024, 12, 3),
    ),
    TechVersionGroundTruth(
        tech=LibraryIdentifier(package_manager=PackageManager.PYPI, name="fastapi"),
        version="0.115.8",
        release_date=date(2025, 1, 30),
    ),
    TechVersionGroundTruth(
        tech=LibraryIdentifier(package_manager=PackageManager.PYPI, name="django"),
        version="5.1.6",
        release_date=date(2025, 2, 5),
    ),
    TechVersionGroundTruth(
        tech=LibraryIdentifier(package_manager=PackageManager.PYPI, name="sqlalchemy"),
        version="2.0.37",
        release_date=date(2025, 1, 10),
    ),
    TechVersionGroundTruth(
        tech=LibraryIdentifier(package_manager=PackageManager.PYPI, name="pydantic"),
        version="2.10.6",
        release_date=date(2025, 1, 24),
    ),
    ### Javascript ###
    TechVersionGroundTruth(
        tech=LibraryIdentifier(package_manager=PackageManager.NPM, name="axios"),
        version="1.7.9",
        release_date=date(2024, 12, 4),
    ),
    TechVersionGroundTruth(
        tech=LibraryIdentifier(package_manager=PackageManager.NPM, name="react"),
        version="19.0.0",
        release_date=date(2024, 12, 5),
    ),
    TechVersionGroundTruth(
        tech=LibraryIdentifier(package_manager=PackageManager.NPM, name="typescript"),
        version="5.7.3",
        release_date=date(2025, 1, 8),
    ),
]
