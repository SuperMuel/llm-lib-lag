from __future__ import annotations
import requests
from bs4 import BeautifulSoup
from functools import lru_cache
from datetime import datetime, date
from bs4.element import Tag

_RUBY_VERSIONS = {
    "3.2.7": date(2025, 2, 4),
    "3.3.7": date(2025, 1, 15),
    "3.4.1": date(2024, 12, 25),
    "3.4.0": date(2024, 12, 25),
    "3.3.6": date(2024, 11, 5),
    "3.2.6": date(2024, 10, 30),
    "3.3.5": date(2024, 9, 3),
    "3.2.5": date(2024, 7, 26),
    "3.3.4": date(2024, 7, 9),
    "3.3.3": date(2024, 6, 12),
    "3.3.2": date(2024, 5, 30),
    "3.1.6": date(2024, 5, 29),
    "3.3.1": date(2024, 4, 23),
    "3.2.4": date(2024, 4, 23),
    "3.1.5": date(2024, 4, 23),
    "3.0.7": date(2024, 4, 23),
    "3.2.3": date(2024, 1, 18),
    "3.3.0": date(2023, 12, 25),
    "3.2.2": date(2023, 3, 30),
    "3.1.4": date(2023, 3, 30),
    "3.0.6": date(2023, 3, 30),
    "2.7.8": date(2023, 3, 30),
    "3.2.1": date(2023, 2, 8),
    "3.2.0": date(2022, 12, 25),
    "3.1.3": date(2022, 11, 24),
    "3.0.5": date(2022, 11, 24),
    "2.7.7": date(2022, 11, 24),
    "3.1.2": date(2022, 4, 12),
    "3.0.4": date(2022, 4, 12),
    "2.7.6": date(2022, 4, 12),
    "2.6.10": date(2022, 4, 12),
    "3.1.1": date(2022, 2, 18),
    "3.1.0": date(2021, 12, 25),
    "3.0.3": date(2021, 11, 24),
    "2.7.5": date(2021, 11, 24),
    "2.6.9": date(2021, 11, 24),
    "3.0.2": date(2021, 7, 7),
    "2.7.4": date(2021, 7, 7),
    "2.6.8": date(2021, 7, 7),
    "3.0.1": date(2021, 4, 5),
    "2.7.3": date(2021, 4, 5),
    "2.6.7": date(2021, 4, 5),
    "2.5.9": date(2021, 4, 5),
    "3.0.0": date(2020, 12, 25),
    "2.7.2": date(2020, 10, 2),
    "2.7.1": date(2020, 3, 31),
    "2.6.6": date(2020, 3, 31),
    "2.5.8": date(2020, 3, 31),
    "2.4.10": date(2020, 3, 31),
    "2.7.0": date(2019, 12, 25),
    "2.4.9": date(2019, 10, 2),
    "2.6.5": date(2019, 10, 1),
    "2.5.7": date(2019, 10, 1),
    "2.4.8": date(2019, 10, 1),
    "2.6.4": date(2019, 8, 28),
    "2.5.6": date(2019, 8, 28),
    "2.4.7": date(2019, 8, 28),
    "2.6.3": date(2019, 4, 17),
    "2.4.6": date(2019, 4, 1),
    "2.5.5": date(2019, 3, 15),
    "2.6.2": date(2019, 3, 13),
    "2.5.4": date(2019, 3, 13),
    "2.6.1": date(2019, 1, 30),
    "2.6.0": date(2018, 12, 25),
    "2.5.3": date(2018, 10, 18),
    "2.5.2": date(2018, 10, 17),
    "2.4.5": date(2018, 10, 17),
    "2.3.8": date(2018, 10, 17),
    "2.5.1": date(2018, 3, 28),
    "2.4.4": date(2018, 3, 28),
    "2.3.7": date(2018, 3, 28),
    "2.2.10": date(2018, 3, 28),
    "2.5.0": date(2017, 12, 25),
    "2.4.3": date(2017, 12, 14),
    "2.3.6": date(2017, 12, 14),
    "2.2.9": date(2017, 12, 14),
    "2.4.2": date(2017, 9, 14),
    "2.3.5": date(2017, 9, 14),
    "2.2.8": date(2017, 9, 14),
    "2.3.4": date(2017, 3, 30),
    "2.2.7": date(2017, 3, 28),
    "2.4.1": date(2017, 3, 22),
    "2.4.0": date(2016, 12, 25),
    "2.3.3": date(2016, 11, 21),
    "2.3.2": date(2016, 11, 15),
    "2.2.6": date(2016, 11, 15),
    "2.3.1": date(2016, 4, 26),
    "2.2.5": date(2016, 4, 26),
    "2.1.10": date(2016, 4, 1),
    "2.1.9": date(2016, 3, 30),
    "2.3.0": date(2015, 12, 25),
    "2.2.4": date(2015, 12, 16),
    "2.1.8": date(2015, 12, 16),
    "2.2.3": date(2015, 8, 18),
    "2.1.7": date(2015, 8, 18),
    "2.2.2": date(2015, 4, 13),
    "2.1.6": date(2015, 4, 13),
    "2.2.1": date(2015, 3, 3),
    "2.2.0": date(2014, 12, 25),
    "2.1.5": date(2014, 11, 13),
    "2.1.4": date(2014, 10, 27),
    "2.1.3": date(2014, 9, 19),
    "2.1.2": date(2014, 5, 9),
    "2.1.1": date(2014, 2, 24),
    "2.1.0": date(2013, 12, 25),
    "2.0.0": date(2013, 2, 24),
    "1.9.3": date(2011, 10, 31),
    "1.9.2": date(2010, 8, 18),
    "1.9.1": date(2009, 1, 30),
    "1.8.7": date(2008, 5, 31),
    "1.9.0": date(2007, 12, 25),
    "1.8.6": date(2007, 3, 12),
    "1.8.5": date(2006, 8, 29),
    "1.8.4": date(2005, 12, 24),
    "1.8.3": date(2005, 9, 21),
    "1.8.2": date(2004, 12, 26),
    "1.8.0": date(2003, 8, 4),
    "1.6.7": date(2002, 3, 1),
}


# -------------------------------------------------------------
# 1. HTML Parsing
# -------------------------------------------------------------
def parse_ruby_releases(html: str) -> dict[str, date]:
    """
    Return a dict mapping:
        "3.2.7" -> date(2025, 2, 4),
        "3.4.1" -> date(2024, 12, 25),
        "3.4.0-preview2" -> date(2024, 10, 7),
        etc.
    from the ruby-lang.org downloads/releases page HTML.

    We do NOT skip RC/preview entries here; we store them all.
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="release-list")
    if not table:
        raise RuntimeError("Could not find a table with class='release-list'.")

    releases: dict[str, date] = {}
    if not isinstance(table, Tag):
        raise RuntimeError("Expected table to be a Tag")

    tbody = table.find("tbody")
    if tbody is not None and isinstance(tbody, Tag):
        rows = tbody.find_all("tr")
    else:
        rows = table.find_all("tr")

    for row in rows:
        if not isinstance(row, Tag):
            continue

        cells = row.find_all("td")
        if len(cells) < 2:
            continue

        version_text = cells[0].get_text(strip=True)  # e.g. "Ruby 3.4.1"
        date_text = cells[1].get_text(strip=True)  # e.g. "2024-12-25"

        if version_text.lower().startswith("ruby "):
            version_str = version_text[5:].strip()
        else:
            version_str = version_text

        try:
            release_dt = datetime.strptime(date_text, "%Y-%m-%d").date()
        except ValueError:
            raise RuntimeError(
                f"Could not parse date {date_text} for version {version_str}"
            )

        releases[version_str] = release_dt

    return releases


# -------------------------------------------------------------
# 2. Cached Fetcher
# -------------------------------------------------------------
@lru_cache(maxsize=1)
def fetch_ruby_releases() -> dict[str, date]:
    """
    Fetch the Ruby releases page once and parse it into a dict.
    If called again, returns the cached result unless cleared.

    Returns:
        Dict of version_string -> release_date
    """
    url = "https://www.ruby-lang.org/en/downloads/releases/"
    resp = requests.get(url)
    resp.raise_for_status()
    return parse_ruby_releases(resp.text)


# -------------------------------------------------------------
# 3. Helper: Get a specific version's release date
# -------------------------------------------------------------
def get_ruby_release_date(
    version: str, releases: dict[str, date] | None = None
) -> date:
    """
    Look up the release date for a specific Ruby version string,
    e.g. "3.4.1" or "3.4.0-rc1".

    If `releases` is None, fetch from ruby-lang.org (cached).
    Raises KeyError if version is not found.
    """
    if version in _RUBY_VERSIONS:
        return _RUBY_VERSIONS[version]

    if releases is None:
        releases = fetch_ruby_releases()

    return releases[version]  # KeyError if not present
