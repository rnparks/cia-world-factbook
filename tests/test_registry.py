"""Structural validation tests for the COUNTRY_REGISTRY."""

import json
from importlib import resources
from pathlib import Path

import pytest

from cia_world_factbook._loader import COUNTRY_REGISTRY


DATA_DIR = Path("src/cia_world_factbook/data")

EXPECTED_REGIONS = [
    "africa",
    "antarctica",
    "australia-oceania",
    "central-america-n-caribbean",
    "central-asia",
    "east-n-southeast-asia",
    "europe",
    "middle-east",
    "north-america",
    "south-america",
    "south-asia",
    "world",
]

EXPECTED_COUNTS_PER_REGION = {
    "africa": 56,
    "antarctica": 4,
    "australia-oceania": 30,
    "central-america-n-caribbean": 33,
    "central-asia": 6,
    "east-n-southeast-asia": 22,
    "europe": 55,
    "middle-east": 19,
    "north-america": 7,
    "south-america": 14,
    "south-asia": 9,
    "world": 1,
}


def _get_all_json_files() -> list[tuple[str, str]]:
    """Return all (region, code) pairs from the data directory."""
    results = []
    for region_dir in DATA_DIR.iterdir():
        if not region_dir.is_dir():
            continue
        for f in region_dir.glob("[a-z][a-z].json"):
            results.append((region_dir.name, f.stem))
    return results


def _get_registry_codes() -> set[str]:
    """Return the set of 2-letter codes in the registry (not aliases)."""
    return {code for code, (_, stem) in COUNTRY_REGISTRY.items() if code == stem}


class TestRegistryCompleteness:
    def test_every_json_file_has_registry_entry(self) -> None:
        missing = []
        for region, code in _get_all_json_files():
            if code not in COUNTRY_REGISTRY:
                missing.append(f"{region}/{code}")
        assert not missing, f"JSON files without registry entries: {missing}"

    def test_every_registry_entry_has_json_file(self) -> None:
        missing = []
        for key, (region, code) in COUNTRY_REGISTRY.items():
            json_path = DATA_DIR / region / f"{code}.json"
            if not json_path.exists():
                missing.append(f"{key} -> {region}/{code}.json")
        assert not missing, f"Registry entries without JSON files: {missing}"

    def test_total_country_count(self) -> None:
        codes = _get_registry_codes()
        assert len(codes) == 256

    def test_total_registry_entries_with_aliases(self) -> None:
        assert len(COUNTRY_REGISTRY) >= 400  # codes + friendly names + manual aliases


class TestRegistryStructure:
    def test_all_keys_are_lowercase(self) -> None:
        non_lower = [k for k in COUNTRY_REGISTRY if k != k.lower()]
        assert not non_lower, f"Non-lowercase registry keys: {non_lower}"

    def test_all_values_are_tuples(self) -> None:
        for key, value in COUNTRY_REGISTRY.items():
            assert isinstance(value, tuple) and len(value) == 2, (
                f"Registry[{key!r}] = {value!r}, expected (region, code) tuple"
            )

    def test_all_codes_are_two_letters(self) -> None:
        for _, (_, code) in COUNTRY_REGISTRY.items():
            assert len(code) == 2 and code.isalpha() and code.islower(), (
                f"Invalid code: {code!r}"
            )

    def test_no_empty_regions(self) -> None:
        for region_dir in DATA_DIR.iterdir():
            if not region_dir.is_dir():
                continue
            files = list(region_dir.glob("[a-z][a-z].json"))
            assert len(files) > 0, f"Empty region directory: {region_dir.name}"


class TestRegions:
    def test_all_expected_regions_present(self) -> None:
        registry_regions = {region for region, _ in COUNTRY_REGISTRY.values()}
        for region in EXPECTED_REGIONS:
            assert region in registry_regions, f"Missing region: {region}"

    def test_no_unexpected_regions(self) -> None:
        registry_regions = {region for region, _ in COUNTRY_REGISTRY.values()}
        unexpected = registry_regions - set(EXPECTED_REGIONS)
        assert not unexpected, f"Unexpected regions: {unexpected}"

    @pytest.mark.parametrize("region, expected_count", EXPECTED_COUNTS_PER_REGION.items())
    def test_region_country_count(self, region: str, expected_count: int) -> None:
        json_files = list((DATA_DIR / region).glob("[a-z][a-z].json"))
        assert len(json_files) == expected_count, (
            f"{region}: expected {expected_count}, got {len(json_files)}"
        )


class TestAliases:
    def test_friendly_name_resolves_to_same_code(self) -> None:
        # Spot-check some aliases
        aliases = {
            "usa": "us",
            "united_states": "us",
            "canada": "ca",
            "germany": "gm",
            "japan": "ja",
            "brazil": "br",
            "australia": "as",
            "india": "in",
            "china": "ch",
            "france": "fr",
        }
        for alias, expected_code in aliases.items():
            assert alias in COUNTRY_REGISTRY, f"Alias {alias!r} not in registry"
            _, code = COUNTRY_REGISTRY[alias]
            assert code == expected_code, (
                f"Alias {alias!r} -> code {code!r}, expected {expected_code!r}"
            )

    def test_all_aliases_point_to_valid_codes(self) -> None:
        codes = _get_registry_codes()
        for key, (region, code) in COUNTRY_REGISTRY.items():
            assert code in codes, (
                f"Alias {key!r} points to unknown code {code!r}"
            )


class TestJsonDataIntegrity:
    def test_all_json_files_are_valid_json(self) -> None:
        invalid = []
        for region, code in _get_all_json_files():
            path = DATA_DIR / region / f"{code}.json"
            try:
                with open(path, encoding="utf-8") as f:
                    json.load(f)
            except json.JSONDecodeError:
                invalid.append(f"{region}/{code}.json")
        assert not invalid, f"Invalid JSON files: {invalid}"

    def test_all_json_files_have_top_level_dict(self) -> None:
        non_dict = []
        for region, code in _get_all_json_files():
            path = DATA_DIR / region / f"{code}.json"
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                non_dict.append(f"{region}/{code}.json")
        assert not non_dict, f"Non-dict top-level JSON: {non_dict}"

    def test_most_countries_have_geography_section(self) -> None:
        """Most countries should have a Geography section."""
        missing = []
        for region, code in _get_all_json_files():
            path = DATA_DIR / region / f"{code}.json"
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if "Geography" not in data and region not in ("world",):
                missing.append(f"{region}/{code}")
        # Allow a few territories to lack Geography
        assert len(missing) <= 5, f"Too many without Geography: {missing}"
