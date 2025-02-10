from datetime import date, datetime
from typing import Literal

import requests


def fetch_github_latest_tag(
    org: str,
    repo: str,
    version_key: Literal["tag_name", "name"] = "tag_name",
    date_key: Literal["published_at", "created_at"] = "published_at",
) -> tuple[str, date]:
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
        -> ("1.84.1", date(2025, 1, 31))
    """
    api_url = f"https://api.github.com/repos/{org}/{repo}/releases/latest"
    resp = requests.get(api_url)
    resp.raise_for_status()

    data = resp.json()
    version_tag = data[version_key]  # e.g. "1.84.1" for rust-lang/rust
    published_at = data[date_key]  # e.g. "2025-01-31T01:59:23Z"

    # Convert the timestamp to a Python datetime
    release_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))

    return version_tag, release_date.date()


def fetch_github_release_date(
    org: str,
    repo: str,
    tag: str,
    date_key: Literal["published_at", "created_at"] = "published_at",
) -> date:
    url = f"https://api.github.com/repos/{org}/{repo}/releases/tags/{tag}"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    published_at = data[date_key].replace("Z", "+00:00")
    return datetime.fromisoformat(published_at).date()
