"""End-to-end tests for the public API."""

import pytest


class TestImport:
    def test_import_us(self) -> None:
        from cia_world_factbook import us
        assert "Geography" in us

    def test_import_canada(self) -> None:
        from cia_world_factbook import ca
        assert "Geography" in ca

    def test_import_germany(self) -> None:
        from cia_world_factbook import gm
        assert "Geography" in gm

    def test_import_japan(self) -> None:
        from cia_world_factbook import ja
        assert "Geography" in ja

    def test_import_brazil(self) -> None:
        from cia_world_factbook import br
        assert "Geography" in br

    def test_import_france(self) -> None:
        from cia_world_factbook import fr
        assert "Geography" in fr

    def test_import_by_friendly_name(self) -> None:
        from cia_world_factbook import australia
        assert "Geography" in australia

    def test_import_nonexistent_raises(self) -> None:
        with pytest.raises((AttributeError, ImportError)):
            from cia_world_factbook import atlantis  # noqa: F401


class TestTraversal:
    def test_attribute_traversal(self) -> None:
        from cia_world_factbook import us
        text = us.geography.location.text
        assert "North America" in text

    def test_dict_traversal(self) -> None:
        from cia_world_factbook import us
        text = us["People and Society"]["Population"]["total"]["text"]
        assert "est." in text

    def test_mixed_access(self) -> None:
        from cia_world_factbook import us
        capital = us.government["Capital"]["name"].text
        assert "Washington" in capital

    def test_str_on_leaf(self) -> None:
        from cia_world_factbook import us
        s = str(us.geography.location)
        assert "North America" in s


class TestLoadCountryFunction:
    def test_load_by_code(self) -> None:
        from cia_world_factbook import load_country
        us = load_country("us")
        assert us.geography.location.text

    def test_load_by_friendly_name(self) -> None:
        from cia_world_factbook import load_country
        au = load_country("australia")
        assert "Oceania" in au.geography.location.text

    def test_load_keyword_code_india(self) -> None:
        from cia_world_factbook import load_country
        india = load_country("in")
        assert isinstance(india.geography.location.text, str)

    def test_load_keyword_code_israel(self) -> None:
        from cia_world_factbook import load_country
        israel = load_country("is")
        assert isinstance(israel.geography.location.text, str)

    def test_load_keyword_code_australia(self) -> None:
        from cia_world_factbook import load_country
        au = load_country("as")
        assert isinstance(au.geography.location.text, str)


class TestListFunctions:
    def test_list_countries_returns_list(self) -> None:
        from cia_world_factbook import list_countries
        codes = list_countries()
        assert isinstance(codes, list)
        assert len(codes) == 256

    def test_list_countries_are_two_letter(self) -> None:
        from cia_world_factbook import list_countries
        for code in list_countries():
            assert len(code) == 2 and code.isalpha()

    def test_list_countries_includes_us(self) -> None:
        from cia_world_factbook import list_countries
        assert "us" in list_countries()

    def test_list_regions_returns_list(self) -> None:
        from cia_world_factbook import list_regions
        regions = list_regions()
        assert isinstance(regions, list)
        assert len(regions) == 12

    def test_list_regions_includes_all(self) -> None:
        from cia_world_factbook import list_regions
        regions = list_regions()
        assert "africa" in regions
        assert "europe" in regions
        assert "world" in regions


class TestSearchFunction:
    def test_search_by_name(self) -> None:
        from cia_world_factbook import search
        results = search("korea")
        codes = [r[0] for r in results]
        assert "kn" in codes
        assert "ks" in codes

    def test_search_by_code(self) -> None:
        from cia_world_factbook import search
        results = search("us")
        codes = [r[0] for r in results]
        assert "us" in codes

    def test_search_case_insensitive(self) -> None:
        from cia_world_factbook import search
        lower = search("japan")
        upper = search("JAPAN")
        assert len(lower) == len(upper)

    def test_search_no_results(self) -> None:
        from cia_world_factbook import search
        assert search("zzzznotacountry") == []

    def test_search_returns_tuples(self) -> None:
        from cia_world_factbook import search
        results = search("france")
        assert len(results) > 0
        code, name, region = results[0]
        assert code == "fr"
        assert region == "europe"


class TestInfoFunction:
    def test_info_returns_string(self) -> None:
        from cia_world_factbook import info
        table = info()
        assert isinstance(table, str)
        assert "Code" in table
        assert "Region" in table

    def test_info_contains_countries(self) -> None:
        from cia_world_factbook import info
        table = info()
        assert "united_states" in table or "us" in table
        assert "africa" in table


class TestCompareFunction:
    def test_compare_returns_dict_with_all_countries(self) -> None:
        from cia_world_factbook import compare
        result = compare("government.capital.name")
        assert isinstance(result, dict)
        assert len(result) == 256

    def test_compare_known_value(self) -> None:
        from cia_world_factbook import compare
        result = compare("government.capital.name")
        assert "Washington" in result["us"]

    def test_compare_missing_path_returns_none(self) -> None:
        from cia_world_factbook import compare
        result = compare("economy.gdp_official_exchange_rate")
        # Antarctica has no GDP
        assert result["ay"] is None

    def test_compare_invalid_path_all_none(self) -> None:
        from cia_world_factbook import compare
        result = compare("fake.nonexistent.path")
        assert all(v is None for v in result.values())

    def test_compare_branch_path(self) -> None:
        from cia_world_factbook import compare
        result = compare("geography")
        # Should return FactbookDict, not a string
        assert result["us"] is not None
        assert not isinstance(result["us"], str)


class TestModuleDir:
    def test_dir_includes_countries(self) -> None:
        import cia_world_factbook
        d = dir(cia_world_factbook)
        assert "us" in d
        assert "ca" in d
        assert "gm" in d

    def test_dir_includes_functions(self) -> None:
        import cia_world_factbook
        d = dir(cia_world_factbook)
        assert "load_country" in d
        assert "compare" in d
        assert "__version__" in d
