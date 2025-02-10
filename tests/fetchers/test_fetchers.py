from datetime import date

from llm_lib_lag.fetchers.fetchers import (
    fetch_npm_release_date,
    fetch_npm_version_info,
    fetch_pypi_release_date,
    fetch_pypi_version_info,
    fetch_latest_version_and_date,
    fetch_version_date,
)
from llm_lib_lag.models import Language, LibraryIdentifier, PackageManager


def test_npm_latest_react() -> None:
    """Test fetching latest React version from npm"""
    version, release_date = fetch_npm_version_info("react")
    major, _, __ = map(int, version.split(".", 2))
    assert major >= 19
    assert isinstance(release_date, date)


def test_pypi_latest_fastapi() -> None:
    """Test fetching latest FastAPI version from PyPI"""
    version, release_date = fetch_pypi_version_info("fastapi")
    major, minor, _ = map(int, version.split(".", 2))
    assert major > 0 or (major == 0 and minor >= 115)
    assert isinstance(release_date, date)


def test_npm_specific_react_version() -> None:
    """Test fetching specific React version from npm"""
    release_date = fetch_npm_release_date("react", "18.3.1")
    assert release_date == date(2024, 4, 26)


def test_pypi_specific_fastapi_version() -> None:
    """Test fetching specific FastAPI version from PyPI"""
    release_date = fetch_pypi_release_date("fastapi", "0.100.0")
    assert release_date == date(2023, 7, 7)


def test_maven_latest_spring_boot() -> None:
    """Test fetching latest Spring Boot version from Maven"""
    maven_identifier = LibraryIdentifier(
        package_manager=PackageManager.MAVEN,
        name="org.springframework.boot:spring-boot-starter-parent",
    )
    version, release_date = fetch_latest_version_and_date(maven_identifier)
    major, minor, _ = map(int, version.split(".", 2))
    assert major >= 3 or (major == 3 and minor >= 2)
    assert isinstance(release_date, date)


def test_maven_specific_spring_boot_version() -> None:
    """Test fetching specific Spring Boot version from Maven"""
    maven_identifier = LibraryIdentifier(
        package_manager=PackageManager.MAVEN,
        name="org.springframework.boot:spring-boot-starter-parent",
    )
    release_date = fetch_version_date(maven_identifier, "3.2.1")
    assert release_date == date(2023, 12, 21)


def test_ruby_versions() -> None:
    """Test fetching various Ruby version release dates"""
    assert fetch_version_date(Language.RUBY, "3.2.0") == date(2022, 12, 25)
    assert fetch_version_date(Language.RUBY, "2.1.5") == date(2014, 11, 13)
    assert fetch_version_date(Language.RUBY, "1.8.0") == date(2003, 8, 4)
