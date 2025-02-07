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
        version="19.1.5",
        release_date=date(2025, 2, 6),
    ),
    TechVersionGroundTruth(
        tech=LibraryIdentifier(
            package_manager=PackageManager.MAVEN,
            name="org.springframework.boot:spring-boot-starter-parent",
        ),
        version="3.4.2",
        release_date=date(2025, 1, 23),
    ),
    TechVersionGroundTruth(
        tech=Language.RUST,
        version="1.84.1",
        release_date=date(2025, 1, 31),
    ),
    TechVersionGroundTruth(
        tech=Language.PYTHON,
        version="3.13.2",
        release_date=date(2025, 2, 5),
    ),
    TechVersionGroundTruth(
        tech=Language.RUBY,
        version="3.4.1",
        release_date=date(2024, 12, 25),
    ),
]

if __name__ == "__main__":
    from .fetchers import fetch_latest_version_and_date

    # ANSI escape codes for colors
    GREEN = "\033[32m"
    RESET = "\033[0m"
    RED = "\033[31m"

    total_ground_truths = len(GROUND_TRUTHS)
    ground_truths_passed = 0

    for ground_truth in GROUND_TRUTHS:
        try:
            fetched_latest_version, latest_date = fetch_latest_version_and_date(
                ground_truth.tech
            )
        except Exception as e:
            print(
                f"{RED}Error fetching latest version for {ground_truth.tech}: {e}{RESET}"
            )
            continue

        assert fetched_latest_version == ground_truth.version, (
            f"Latest version mismatch for {ground_truth.tech}: Fetched {fetched_latest_version} != Ground truth {ground_truth.version}"
        )
        assert latest_date.date() == ground_truth.release_date, (
            f"Latest date mismatch for {ground_truth.tech}: Fetched {latest_date.date()} != Ground truth {ground_truth.release_date}"
        )
        print(
            f"{GREEN}✓ {ground_truth.tech}: {fetched_latest_version} ({latest_date.date()}){RESET}"
        )
        ground_truths_passed += 1

    if ground_truths_passed == total_ground_truths:
        print(f"{GREEN}All ground truths passed{RESET}")
    else:
        print(
            f"{RED}{ground_truths_passed}/{total_ground_truths} ground truths passed{RESET}"
        )
