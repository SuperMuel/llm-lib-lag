import requests
from datetime import datetime
from src.models import LibraryIdentifier, PackageManager


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


def fetch_latest_version_and_date(
    identifier: LibraryIdentifier,
) -> tuple[str, datetime]:
    """
    Unified function to fetch the latest version info for a LibraryIdentifier,
    handling NPM or PYPI (extendable to other PackageManagers).
    """
    match identifier.package_manager:
        case PackageManager.NPM:
            return fetch_npm_version_info(identifier.name)
        case PackageManager.PYPI:
            return fetch_pypi_version_info(identifier.name)
        # Add more logic for other package managers (MAVEN, etc.)
        case _:
            raise ValueError(
                f"Unsupported package manager: {identifier.package_manager}"
            )


def fetch_version_date(identifier: LibraryIdentifier, version: str) -> datetime:
    """
    Fetch the release date of a specific version from the registry.
    """
    match identifier.package_manager:
        case PackageManager.NPM:
            return fetch_npm_release_date(identifier.name, version)
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

    print()

    # -------------------------------------------------------------------------
    # 2. Latest FastAPI version (PyPI)
    # -------------------------------------------------------------------------
    print("Latest fastapi version:")
    fastapi_latest_ver, fastapi_latest_dt = fetch_pypi_version_info("fastapi")
    print(f"  version={fastapi_latest_ver}, released={fastapi_latest_dt}")

    print()

    # -------------------------------------------------------------------------
    # 3. Release date of react@18.3.1
    # -------------------------------------------------------------------------
    print("Release date of react@18.3.1:")
    try:
        react_1831_dt = fetch_npm_release_date("react", "18.3.1")
        print(f"  react@18.3.1 released={react_1831_dt}")
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
    except ValueError as e:
        print(f"  Could not fetch fastapi@0.100.0: {e}")
