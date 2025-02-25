from datetime import date
import logging
from .models import Language, TechVersionGroundTruth, LibraryIdentifier, PackageManager

logger = logging.getLogger(__name__)


GROUND_TRUTHS = [
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
        version="2.0.38",
        release_date=date(2025, 2, 6),
    ),
    TechVersionGroundTruth(
        tech=LibraryIdentifier(package_manager=PackageManager.PYPI, name="pydantic"),
        version="2.10.6",
        release_date=date(2025, 1, 24),
    ),
    TechVersionGroundTruth(
        tech=LibraryIdentifier(package_manager=PackageManager.PYPI, name="langchain"),
        version="0.3.19",
        release_date=date(2025, 2, 17),
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
    TechVersionGroundTruth(
        tech=LibraryIdentifier(package_manager=PackageManager.NPM, name="vue"),
        version="3.5.13",
        release_date=date(2024, 11, 15),
    ),
    TechVersionGroundTruth(
        tech=LibraryIdentifier(
            package_manager=PackageManager.NPM, name="@angular/core"
        ),
        version="19.1.7",
        release_date=date(2025, 2, 19),
    ),
    TechVersionGroundTruth(
        tech=LibraryIdentifier(
            package_manager=PackageManager.MAVEN,
            name="org.springframework.boot:spring-boot-starter-parent",
        ),
        version="3.4.3",
        release_date=date(2025, 2, 20),
    ),
    TechVersionGroundTruth(
        tech=Language.RUST,
        version="1.85.0",
        release_date=date(2025, 2, 20),
    ),
    TechVersionGroundTruth(
        tech=Language.PYTHON,
        version="3.13.2",
        release_date=date(2025, 2, 5),
    ),
    TechVersionGroundTruth(
        tech=Language.RUBY,
        version="3.4.2",
        release_date=date(2025, 2, 14),
    ),
    TechVersionGroundTruth(
        tech=Language.DOTNET,
        version="9.0.2",
        release_date=date(2025, 2, 11),
    ),
]
