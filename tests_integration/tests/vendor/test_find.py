"""Integration tests for the Vendor API endpoint."""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import httpx
import pytest

URL = "http://spoolman:8000"


def vendor_lists_equal(a: Iterable[dict[str, Any]], b: Iterable[dict[str, Any]]) -> bool:
    """Compare two lists of vendors where the order of the vendors is not guaranteed."""
    return sorted(a, key=lambda x: x["id"]) == sorted(b, key=lambda x: x["id"])


@dataclass
class Fixture:
    vendors: list[dict[str, Any]]


@pytest.fixture(scope="module")
def vendors() -> Iterable[Fixture]:
    """Add some vendors to the database."""
    result = httpx.post(
        f"{URL}/api/v1/vendor",
        json={"name": "John", "comment": "abcdefghåäö"},
    )
    result.raise_for_status()
    vendor_1 = result.json()

    result = httpx.post(
        f"{URL}/api/v1/vendor",
        json={"name": "Stan", "comment": "gfdadfg"},
    )
    result.raise_for_status()
    vendor_2 = result.json()

    yield Fixture(
        vendors=[vendor_1, vendor_2],
    )

    httpx.delete(f"{URL}/api/v1/vendor/{vendor_1['id']}").raise_for_status()
    httpx.delete(f"{URL}/api/v1/vendor/{vendor_2['id']}").raise_for_status()


def test_find_all_vendors(vendors: Fixture):
    # Execute
    result = httpx.get(
        f"{URL}/api/v1/vendor",
    )
    result.raise_for_status()

    # Verify
    vendors_result = result.json()
    assert vendor_lists_equal(vendors_result, vendors.vendors)


def test_find_vendors_by_name(vendors: Fixture):
    # Execute
    result = httpx.get(
        f"{URL}/api/v1/vendor",
        params={"name": vendors.vendors[0]["name"]},
    )
    result.raise_for_status()

    # Verify
    vendors_result = result.json()
    assert vendors_result == [vendors.vendors[0]]
