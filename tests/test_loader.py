"""Tests for data loading, caching, and country resolution."""

import pytest

from cia_world_factbook._loader import COUNTRY_REGISTRY, load_country, _country_cache
from cia_world_factbook._wrapper import FactbookDict


class TestBasicLoading:
    def test_load_us(self) -> None:
        us = load_country("us")
        assert isinstance(us, FactbookDict)
        assert "Geography" in us

    def test_load_returns_factbook_dict(self) -> None:
        ca = load_country("ca")
        assert isinstance(ca, FactbookDict)

    def test_unknown_country_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown country"):
            load_country("atlantis")

    def test_error_message_lists_available(self) -> None:
        with pytest.raises(ValueError, match="Available:"):
            load_country("zzz")


class TestCaching:
    def test_same_code_returns_same_object(self) -> None:
        a = load_country("us")
        b = load_country("us")
        assert a is b

    def test_aliases_share_underlying_data(self) -> None:
        us = load_country("us")
        usa = load_country("usa")
        united_states = load_country("united_states")
        assert us.to_dict() == usa.to_dict() == united_states.to_dict()


class TestDataIntegrity:
    def test_us_location(self) -> None:
        us = load_country("us")
        loc = us["Geography"]["Location"]["text"]
        assert "North America" in loc

    def test_canada_location(self) -> None:
        ca = load_country("ca")
        assert "North America" in ca.geography.location.text

    def test_germany_capital(self) -> None:
        gm = load_country("gm")
        assert "Berlin" in gm.government.capital.name.text

    def test_japan_area(self) -> None:
        ja = load_country("ja")
        assert "377,915" in ja.geography.area.total.text

    def test_brazil_location(self) -> None:
        br = load_country("br")
        assert "South America" in br.geography.location.text


# Load one country per region to verify all regions work
REGION_SAMPLES = [
    ("ag", "africa"),
    ("ay", "antarctica"),
    ("as", "australia-oceania"),
    ("cu", "central-america-n-caribbean"),
    ("kz", "central-asia"),
    ("ch", "east-n-southeast-asia"),
    ("fr", "europe"),
    ("is", "middle-east"),
    ("us", "north-america"),
    ("br", "south-america"),
    ("in", "south-asia"),
    ("xx", "world"),
]


class TestRegionLoading:
    @pytest.mark.parametrize("code, region", REGION_SAMPLES)
    def test_load_from_region(self, code: str, region: str) -> None:
        country = load_country(code)
        assert isinstance(country, FactbookDict)
        assert len(country) > 0


class TestFriendlyNameLoading:
    @pytest.mark.parametrize(
        "friendly_name",
        [
            "australia",
            "india",
            "israel",
            "canada",
            "germany",
            "japan",
            "brazil",
            "france",
            "china",
            "kenya",
        ],
    )
    def test_load_by_friendly_name(self, friendly_name: str) -> None:
        country = load_country(friendly_name)
        assert isinstance(country, FactbookDict)
        assert len(country) > 0
