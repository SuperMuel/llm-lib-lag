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
    # TechVersionGroundTruth(
    #     tech=LibraryIdentifier(package_manager=PackageManager.NPM, name="vue"),
    #     version="3.3.4",
    #     release_date=date(2024, 11, 20),
    # ),
    # TechVersionGroundTruth(
    #     tech=LibraryIdentifier(package_manager=PackageManager.NPM, name="angular"),
    #     version="15.2.0",
    #     release_date=date(2024, 10, 10),
    # ),
    # TechVersionGroundTruth(
    #     tech=Language.JAVA,
    #     version="21.0.0",  # For example, a Java SE release version
    #     release_date=date(2025, 2, 10),
    # ),
    # TechVersionGroundTruth(
    #     tech=LibraryIdentifier(
    #         package_manager=PackageManager.MAVEN, name="spring-boot"
    #     ),
    #     version="3.1.0",
    #     release_date=date(2025, 1, 20),
    # ),
    # spring boot :
    TechVersionGroundTruth(
        tech=LibraryIdentifier(
            package_manager=PackageManager.MAVEN,
            name="org.springframework.boot:spring-boot-starter-parent",
        ),
        version="3.4.2",
        release_date=date(2025, 1, 23),
    ),
]
