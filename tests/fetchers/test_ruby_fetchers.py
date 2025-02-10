"""Tests for Ruby version fetchers."""

from datetime import date
from unittest.mock import patch

import pytest
from llm_lib_lag.fetchers.ruby_fetchers import (
    get_ruby_release_date,
    fetch_ruby_releases,
)

MOCK_HTML = """<table class="release-list">
<tbody><tr>
<th>Release Version</th>
<th>Release Date</th>
<th>Download URL</th>
<th>Release Notes</th>
</tr>

<tr>
<td>Ruby 3.2.7</td>
<td>2025-02-04</td>
<td><a href="https://cache.ruby-lang.org/pub/ruby/3.2/ruby-3.2.7.tar.gz">download</a></td>
<td><a href="/en/news/2025/02/04/ruby-3-2-7-released/">more...</a></td>
</tr>
<tr>
<td>Ruby 3.4.1</td>
<td>2024-12-25</td>
<td><a href="https://cache.ruby-lang.org/pub/ruby/3.4/ruby-3.4.1.tar.gz">download</a></td>
<td><a href="/en/news/2024/12/25/ruby-3-4-1-released/">more...</a></td>
</tr>
<tr>
<td>Ruby 3.4.0-rc1</td>
<td>2024-12-12</td>
<td><a href="https://cache.ruby-lang.org/pub/ruby/3.4/ruby-3.4.0-rc1.tar.gz">download</a></td>
<td><a href="/en/news/2024/12/12/ruby-3-4-0-rc1-released/">more...</a></td>
</tr>
<tr>
<td>Ruby 2.7.0</td>
<td>2019-12-25</td>
<td><a href="https://cache.ruby-lang.org/pub/ruby/2.7/ruby-2.7.0.tar.gz">download</a></td>
<td><a href="/en/news/2019/12/25/ruby-2-7-0-released/">more...</a></td>
</tr>
<tr>
<td>Ruby 1.8.7</td>
<td>2008-05-31</td>
<td><a href="https://cache.ruby-lang.org/pub/ruby/1.8/ruby-1.8.7.tar.gz">download</a></td>
<td><a href="/en/news/2008/05/31/ruby-1-8-7-has-been-released/">more...</a></td>
</tr>
</tbody></table>"""


@pytest.mark.parametrize(
    "version,expected_date",
    [
        ("3.2.7", date(2025, 2, 4)),
        ("3.4.1", date(2024, 12, 25)),
        ("2.7.0", date(2019, 12, 25)),
        ("1.8.7", date(2008, 5, 31)),
    ],
)
def test_get_ruby_release_date_with_ground_truth(
    version: str, expected_date: date
) -> None:
    """Test that get_ruby_release_date returns correct dates from the ground truth data."""
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = MOCK_HTML

        releases = fetch_ruby_releases()
        assert get_ruby_release_date(version, releases) == expected_date


def test_get_ruby_release_date_invalid_version() -> None:
    """Test that get_ruby_release_date raises KeyError for invalid versions."""
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = MOCK_HTML

        releases = fetch_ruby_releases()

        with pytest.raises(KeyError):
            get_ruby_release_date("99.99.99", releases)


def test_real_fetch_ruby_releases() -> None:
    """Test that fetch_ruby_releases fetches the correct releases."""
    releases = fetch_ruby_releases()
    assert len(releases) > 0
    assert "3.2.7" in releases
    assert "3.4.1" in releases
