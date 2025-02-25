from typing import Any
import os
import requests
from functools import lru_cache
from packaging.version import parse as parse_version
from datetime import date, datetime, UTC
from ..models import Language, LibraryIdentifier, PackageManager
from .ruby_fetchers import get_ruby_release_date
from .util import fetch_github_latest_tag


class LanguageVersionNotFoundError(Exception):
    def __init__(
        self,
        language: Language,
        version: str | None = None,
    ) -> None:
        self.language = language
        self.version = version
        super().__init__(f"Language '{language}' version '{version}' not found")


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


def fetch_npm_version_info(library_name: str) -> tuple[str, date]:
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
    return latest_version, release_dt.date()


def fetch_pypi_version_info(library_name: str) -> tuple[str, date]:
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
    return latest_version, release_dt.date()


def fetch_npm_release_date(library_name: str, version: str) -> date:
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
    return datetime.fromisoformat(release_date_str).date()


def fetch_pypi_release_date(library_name: str, version: str) -> date:
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
    return datetime.fromisoformat(release_date_str).date()


def fetch_maven_version_info(group_id: str, artifact_id: str) -> tuple[str, date]:
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
    return latest_version, release_dt.date()


def fetch_maven_release_date(group_id: str, artifact_id: str, version: str) -> date:
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
    return datetime.fromtimestamp(ts_millis / 1000, UTC).date()


# def fetch_nodejs_latest_stable() -> tuple[str, date]:
#     """Fetch the latest stable Node.js version"""
#     url = "https://nodejs.org/dist/index.json"
#     response = requests.get(url)
#     response.raise_for_status()
#     releases = response.json()
#     lts_releases = [r for r in releases if r["lts"] is not False]
#     latest = max(lts_releases, key=lambda x: x["date"])
#     version = latest["version"].lstrip("v")
#     release_date = datetime.fromisoformat(latest["date"]).date()
#     return version, release_date


def get_dotnet_latest_stable() -> tuple[str, date]:
    url = "https://api.github.com/repos/dotnet/core/releases"
    headers = {"Accept": "application/vnd.github.v3+json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    releases = response.json()
    for release in releases:
        if (
            not release["prerelease"]
            and not release["draft"]
            and release["tag_name"].startswith("v")
        ):
            version = release["tag_name"].lstrip("v")
            date_str = release["published_at"]
            release_date = datetime.fromisoformat(
                date_str.replace("Z", "+00:00")
            ).date()
            return version, release_date
    raise ValueError("No stable version found for dotnet")


def get_dotnet_specific_version(version: str) -> tuple[str, date]:
    """
    Fetch the specific version of the dotnet release.
    """
    url = "https://api.github.com/repos/dotnet/core/releases"
    headers = {"Accept": "application/vnd.github.v3+json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    releases = response.json()

    for release in releases:
        if (
            release["tag_name"].lstrip("v") == version
            and not release["prerelease"]
            and not release["draft"]
        ):
            date_str = release["published_at"]
            release_date = datetime.fromisoformat(
                date_str.replace("Z", "+00:00")
            ).date()
            return version, release_date

    raise LibraryVersionNotFoundError("dotnet", version=version, package_manager=None)


@lru_cache(maxsize=1)
def _fetch_python_versions_manifest() -> list[dict[str, Any]]:
    """
    Fetch and cache the Python versions manifest from GitHub Actions.
    The cache is invalidated after the first call and will be refreshed on the next call.
    """
    manifest_url = "https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json"
    response = requests.get(manifest_url)
    response.raise_for_status()
    versions = response.json()

    # Assert versions are in descending order by version number
    for i in range(len(versions) - 1):
        curr_version = parse_version(versions[i]["version"])
        next_version = parse_version(versions[i + 1]["version"])
        assert curr_version > next_version, (
            f"Versions not in descending order: {versions[i]['version']} <= {versions[i + 1]['version']}"
        )

    return versions


def fetch_python_latest_stable() -> tuple[str, date]:
    """
    Fetch the latest stable Python version and its release date using the
    actions/python-versions manifest and GitHub API.
    """
    versions = _fetch_python_versions_manifest()

    # Filter for stable versions (exclude any versions containing 'rc', 'beta', or 'alpha')
    stable_versions = [
        v
        for v in versions
        if v.get("stable") is True
        and not any(x in v["version"].lower() for x in ["rc", "beta", "alpha"])
    ]

    if not stable_versions:
        raise ValueError("No stable Python versions found.")

    # Sort stable versions in descending order by version number
    stable_versions = sorted(
        stable_versions, key=lambda v: parse_version(v["version"]), reverse=True
    )
    latest = stable_versions[0]
    latest_version = latest["version"]
    release_url = latest["release_url"]

    # Convert the GitHub release URL to the GitHub API URL
    # e.g. "https://github.com/actions/python-versions/releases/tag/3.13.2-13149511920"
    # becomes "https://api.github.com/repos/actions/python-versions/releases/tags/3.13.2-13149511920"
    api_url = release_url.replace("github.com", "api.github.com/repos").replace(
        "/tag/", "/tags/"
    )

    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    api_resp = requests.get(api_url, headers=headers)
    api_resp.raise_for_status()
    release_data = api_resp.json()
    published_at = release_data.get("published_at")
    if not published_at:
        raise ValueError(
            f"Could not find 'published_at' in release data for Python {latest_version}"
        )

    release_date = datetime.fromisoformat(published_at.replace("Z", "+00:00")).date()
    return latest_version, release_date


def fetch_python_version_date(version: str) -> date:
    """
    Fetch the release date of a specific Python version using the actions/python-versions manifest.

    Args:
        version: The Python version to look up (e.g. "3.12.0")

    Returns:
        The release date of the specified version

    Raises:
        LibraryVersionNotFoundError: If the specified version is not found
    """
    versions = _fetch_python_versions_manifest()

    # Find the exact version match
    matching_versions = [v for v in versions if v["version"] == version]
    if not matching_versions:
        raise LibraryVersionNotFoundError("python", version=version)

    version_info = matching_versions[0]
    release_url = version_info["release_url"]

    # Convert GitHub release URL to API URL
    api_url = release_url.replace("github.com", "api.github.com/repos").replace(
        "/tag/", "/tags/"
    )
    print(api_url)

    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    api_resp = requests.get(api_url, headers=headers)
    api_resp.raise_for_status()
    release_data = api_resp.json()

    print(release_data)

    published_at = release_data.get("published_at")
    if not published_at:
        raise ValueError(
            f"Could not find 'published_at' in release data for Python {version}"
        )

    return datetime.fromisoformat(published_at.replace("Z", "+00:00")).date()


def fetch_latest_version_and_date(
    tech: LibraryIdentifier | Language,
) -> tuple[str, date]:
    """
    Unified function to fetch the latest version info for a LibraryIdentifier,
    handling NPM or PYPI (extendable to other PackageManagers).
    """
    if isinstance(tech, Language):
        match tech:
            # case Language.NODEJS:
            #     return fetch_nodejs_latest_stable()
            # case Language.GO:
            #     return fetch_go_latest_stable()
            # case Language.JAVA:
            #     return fetch_java_latest_stable()
            # case Language.C_SHARP:
            #     return get_c_sharp_latest_stable()
            case Language.RUST:
                return fetch_github_latest_tag(
                    "rust-lang", "rust", version_key="tag_name"
                )
            case Language.RUBY:
                return fetch_github_latest_tag(
                    "ruby", "ruby", version_key="name", date_key="created_at"
                )
            case Language.DOTNET:
                return get_dotnet_latest_stable()
            case Language.PYTHON:
                return fetch_python_latest_stable()
        raise ValueError(f"Unsupported language: {tech} to fetch latest version info")

    match tech.package_manager:
        case PackageManager.NPM:
            return fetch_npm_version_info(tech.name)
        case PackageManager.MAVEN:
            group_id, artifact_id = tech.name.split(":", 1)
            return fetch_maven_version_info(group_id, artifact_id)
        case PackageManager.PYPI:
            return fetch_pypi_version_info(tech.name)

    raise ValueError(
        f"Unsupported package manager: {tech.package_manager} to fetch latest version info"
    )


def fetch_version_date(identifier: LibraryIdentifier | Language, version: str) -> date:
    """
    Fetch the release date of a specific version from the registry.
    """
    if isinstance(identifier, Language):
        match identifier:
            case Language.RUBY:
                assert not version.startswith("v"), (
                    "Ruby version should not start with 'v'"
                )
                return get_ruby_release_date(version)
            case Language.PYTHON:
                return fetch_python_version_date(version)
        raise ValueError(f"Unsupported language: {identifier} to fetch version date")
    match identifier.package_manager:
        case PackageManager.NPM:
            return fetch_npm_release_date(identifier.name, version)
        case PackageManager.MAVEN:
            group_id, artifact_id = identifier.name.split(":", 1)
            return fetch_maven_release_date(group_id, artifact_id, version)
        case PackageManager.PYPI:
            return fetch_pypi_release_date(identifier.name, version)

    raise ValueError(
        f"Unsupported package manager: {identifier.package_manager} to fetch version date"
    )
