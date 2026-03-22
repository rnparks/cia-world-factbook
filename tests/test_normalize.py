import pytest

from cia_world_factbook._wrapper import _normalize_key


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Geography", "geography"),
        ("People and Society", "people_and_society"),
        ("Area - comparative", "area_comparative"),
        ("freshwater lake(s)", "freshwater_lake_s"),
        ("GDP - composition, by sector", "gdp_composition_by_sector"),
        ("0-14 years", "_0_14_years"),
        ("  total  ", "total"),
        ("Military & Security", "military_and_security"),
        ("Life expectancy at birth", "life_expectancy_at_birth"),
        ("text", "text"),
        ("A--B", "a_b"),
    ],
)
def test_normalize_key(raw: str, expected: str) -> None:
    assert _normalize_key(raw) == expected
