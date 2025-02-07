from typing import Literal
import requests
from datetime import date, datetime, UTC
from .models import Language, LibraryIdentifier, PackageManager


class LibraryVersionNotFoundError(Exception):
    def __init__(
        self,
        library_name: str,
        version: str | None = None,
        package_manager: PackageManager | None = None,
    ) -> None:
        self.library_name = library_name
        self.version = version
        self.package_manager = package_manager
        super().__init__(
            f"Library '{library_name}' version '{version}' not found in {package_manager}"
        )


def fetch_npm_version_info(library_name: str) -> tuple[str, datetime]:
    """
    Fetch the latest version and release date from npm registry for the given library.
    """
    url = f"https://registry.npmjs.org/{library_name}"
    response = requests.get(url)
    if response.status_code == 404:
        raise LibraryVersionNotFoundError(
            library_name, package_manager=PackageManager.NPM
        )
    response.raise_for_status()
    data = response.json()

    latest_version = data["dist-tags"]["latest"]
    # 'time' is a dict of version -> isoDate
    release_date_str = data["time"][latest_version].replace("Z", "+00:00")
    release_dt = datetime.fromisoformat(release_date_str)
    return latest_version, release_dt


def fetch_pypi_version_info(library_name: str) -> tuple[str, datetime]:
    """
    Fetch the latest version and release date from PyPI for the given library.
    """
    url = f"https://pypi.org/pypi/{library_name}/json"
    response = requests.get(url)
    if response.status_code == 404:
        raise LibraryVersionNotFoundError(library_name)
    response.raise_for_status()
    data = response.json()

    latest_version = data["info"]["version"]
    release_files = data["releases"].get(latest_version, [])
    if not release_files:
        raise ValueError(f"No release info found for {library_name}=={latest_version}")

    # Typically the last file object has the correct 'upload_time_iso_8601'
    release_file = release_files[-1]
    release_date_str = release_file["upload_time_iso_8601"].replace("Z", "+00:00")
    release_dt = datetime.fromisoformat(release_date_str)
    return latest_version, release_dt


def fetch_npm_release_date(library_name: str, version: str) -> datetime:
    """
    Fetch the release date of a specific version from the npm registry.
    """
    url = f"https://registry.npmjs.org/{library_name}"
    response = requests.get(url)
    if response.status_code == 404:
        raise LibraryVersionNotFoundError(
            library_name, version=version, package_manager=PackageManager.NPM
        )
    response.raise_for_status()
    data = response.json()

    # 'time' is a dict of version -> isoDate
    if version not in data["time"]:
        raise LibraryVersionNotFoundError(
            library_name, version=version, package_manager=PackageManager.NPM
        )
    release_date_str = data["time"][version].replace("Z", "+00:00")
    return datetime.fromisoformat(release_date_str)


def fetch_pypi_release_date(library_name: str, version: str) -> datetime:
    """
    Fetch the release date of a specific version from PyPI.
    """
    url = f"https://pypi.org/pypi/{library_name}/{version}/json"
    response = requests.get(url)
    if response.status_code == 404:
        raise LibraryVersionNotFoundError(
            library_name, version=version, package_manager=PackageManager.PYPI
        )
    response.raise_for_status()
    data = response.json()

    files = data["urls"]
    if not files:
        raise ValueError(
            f"No files found for {library_name}=={version}; cannot determine release date."
        )
    # Typically the first file or the last file has 'upload_time_iso_8601'
    release_date_str = files[-1]["upload_time_iso_8601"].replace("Z", "+00:00")
    return datetime.fromisoformat(release_date_str)


def fetch_maven_version_info(group_id: str, artifact_id: str) -> tuple[str, datetime]:
    """Fetch the latest version and release date from Maven Central for the given artifact."""
    group_path = group_id.replace(".", "/")
    url = (
        f"https://repo1.maven.org/maven2/{group_path}/{artifact_id}/maven-metadata.xml"
    )
    response = requests.get(url)
    if response.status_code == 404:
        raise LibraryVersionNotFoundError(
            f"{group_id}:{artifact_id}", package_manager=PackageManager.MAVEN
        )
    response.raise_for_status()
    import xml.etree.ElementTree as ET

    root = ET.fromstring(response.content)
    versioning = root.find("versioning")
    if versioning is None:
        raise ValueError(f"No versioning info found for {group_id}:{artifact_id}")
    latest_elem = versioning.find("latest")
    if latest_elem is None or latest_elem.text is None:
        raise ValueError(f"No latest version found for {group_id}:{artifact_id}")
    latest_version = latest_elem.text
    last_updated = versioning.find("lastUpdated")
    if last_updated is None or last_updated.text is None:
        raise ValueError(f"No lastUpdated found for {group_id}:{artifact_id}")
    timestamp = last_updated.text
    release_dt = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
    return latest_version, release_dt


def fetch_maven_release_date(group_id: str, artifact_id: str, version: str) -> datetime:
    """Fetch the release date of a specific version from Maven Central using the search.maven.org API."""
    query = f'g:"{group_id}" AND a:"{artifact_id}" AND v:"{version}"'
    url = "https://search.maven.org/solrsearch/select"
    params = {
        "q": query,
        "core": "gav",
        "rows": 1,
        "wt": "json",
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    docs = data.get("response", {}).get("docs", [])
    if not docs:
        raise LibraryVersionNotFoundError(
            f"{group_id}:{artifact_id}",
            version=version,
            package_manager=PackageManager.MAVEN,
        )
    doc = docs[0]
    ts_millis = doc["timestamp"]
    return datetime.fromtimestamp(ts_millis / 1000, UTC)


def fetch_github_latest_tag(
    org: str, repo: str, version_key: Literal["tag_name", "name"] = "tag_name"
) -> tuple[str, datetime]:
    """
    Fetches the latest release for a GitHub repository by calling:
        https://api.github.com/repos/{org_repo}/releases/latest

    Returns a tuple of:
      (version_tag, release_date)

    WARNING:
    - If the repo doesn't have 'latest' releases or if it's not using
      GitHub Releases, this may fail or give unexpected data.
    - The tag_name may not always be semantic versioning.

    Example usage:
      fetch_github_latest_tag("rust-lang", "rust")
        -> ("1.84.1", datetime(2025, 1, 31, 1, 59, 23, tzinfo=UTC))
    """
    api_url = f"https://api.github.com/repos/{org}/{repo}/releases/latest"
    resp = requests.get(api_url)
    resp.raise_for_status()

    data = resp.json()
    version_tag = data[version_key]  # e.g. "1.84.1" for rust-lang/rust
    published_at = data["published_at"]  # e.g. "2025-01-31T01:59:23Z"

    # Convert the timestamp to a Python datetime
    release_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))

    return version_tag, release_date


def fetch_latest_version_and_date(
    tech: LibraryIdentifier | Language,
) -> tuple[str, datetime]:
    """
    Unified function to fetch the latest version info for a LibraryIdentifier,
    handling NPM or PYPI (extendable to other PackageManagers).
    """
    if isinstance(tech, Language):
        match tech:
            case Language.RUST:
                return fetch_github_latest_tag(
                    "rust-lang", "rust", version_key="tag_name"
                )
            case Language.PYTHON:
                return fetch_github_latest_tag(
                    "actions", "python-versions", version_key="name"
                )
            case Language.RUBY:
                return fetch_github_latest_tag("ruby", "ruby", version_key="name")
            case _:
                raise ValueError(f"Unsupported language: {tech}")

    match tech.package_manager:
        case PackageManager.NPM:
            return fetch_npm_version_info(tech.name)
        case PackageManager.MAVEN:
            group_id, artifact_id = tech.name.split(":", 1)
            return fetch_maven_version_info(group_id, artifact_id)
        case PackageManager.PYPI:
            return fetch_pypi_version_info(tech.name)
    raise ValueError(f"Unsupported package manager: {tech.package_manager}")


def fetch_version_date(identifier: LibraryIdentifier, version: str) -> datetime:
    """
    Fetch the release date of a specific version from the registry.
    """
    match identifier.package_manager:
        case PackageManager.NPM:
            return fetch_npm_release_date(identifier.name, version)
        case PackageManager.MAVEN:
            group_id, artifact_id = identifier.name.split(":", 1)
            return fetch_maven_release_date(group_id, artifact_id, version)
        case PackageManager.PYPI:
            return fetch_pypi_release_date(identifier.name, version)
        # Add more logic for other package managers (MAVEN, etc.)
        case _:
            raise ValueError(
                f"Unsupported package manager: {identifier.package_manager}"
            )


if __name__ == "__main__":
    # -------------------------------------------------------------------------
    # 1. Latest React version (npm)
    # -------------------------------------------------------------------------
    print("Latest react version:")
    react_latest_ver, react_latest_dt = fetch_npm_version_info("react")
    print(f"  version={react_latest_ver}, released={react_latest_dt}")
    major, minor, patch = map(int, react_latest_ver.split(".", 2))
    assert major >= 19
    print()

    # -------------------------------------------------------------------------
    # 2. Latest FastAPI version (PyPI)
    # -------------------------------------------------------------------------
    print("Latest fastapi version:")
    fastapi_latest_ver, fastapi_latest_dt = fetch_pypi_version_info("fastapi")
    print(f"  version={fastapi_latest_ver}, released={fastapi_latest_dt}")
    major, minor, patch = map(int, fastapi_latest_ver.split(".", 2))
    assert major > 0 or (major == 0 and minor >= 115)
    print()

    # -------------------------------------------------------------------------
    # 3. Release date of react@18.3.1
    # -------------------------------------------------------------------------
    print("Release date of react@18.3.1:")
    try:
        react_1831_dt = fetch_npm_release_date("react", "18.3.1")
        print(f"  react@18.3.1 released={react_1831_dt}")
        assert react_1831_dt.date() == date(2024, 4, 26)
    except ValueError as e:
        print(f"  Could not fetch react@18.3.1: {e}")

    print()

    # -------------------------------------------------------------------------
    # 4. Release date of fastapi@0.100.0
    # -------------------------------------------------------------------------
    print("Release date of fastapi@0.100.0:")
    try:
        fastapi_100_dt = fetch_pypi_release_date("fastapi", "0.100.0")
        print(f"  fastapi@0.100.0 released={fastapi_100_dt}")
        assert fastapi_100_dt.date() == date(2023, 7, 7)
    except ValueError as e:
        print(f"  Could not fetch fastapi@0.100.0: {e}")

    print()

    # -------------------------------------------------------------------------
    # 5. Latest Maven version (spring-boot-starter-parent)
    # -------------------------------------------------------------------------
    print("Latest Maven version (spring-boot-starter-parent):")
    maven_identifier = LibraryIdentifier(
        package_manager=PackageManager.MAVEN,
        name="org.springframework.boot:spring-boot-starter-parent",
    )
    maven_latest_ver, maven_latest_dt = fetch_latest_version_and_date(maven_identifier)
    print(f"  version={maven_latest_ver}, released={maven_latest_dt}")
    major, minor, patch = map(int, maven_latest_ver.split(".", 2))
    assert major >= 3 or (major == 3 and minor >= 2)

    print()

    # -------------------------------------------------------------------------
    # 6. Release date of Maven artifact version 3.2.1
    # -------------------------------------------------------------------------
    print("Release date of Maven artifact version 3.2.1:")
    try:
        maven_version_date = fetch_version_date(maven_identifier, "3.2.1")
        print(f"  released={maven_version_date}")
        assert maven_version_date.date() == date(2023, 12, 21)
    except Exception as e:
        print(f"  Could not fetch Maven version 3.2.1: {e}")

    print()
