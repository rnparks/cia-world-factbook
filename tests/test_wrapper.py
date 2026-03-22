import pytest

from cia_world_factbook._wrapper import FactbookDict


@pytest.fixture
def sample() -> FactbookDict:
    return FactbookDict(
        {
            "Geography": {
                "Location": {"text": "North America"},
                "Area": {
                    "total ": {"text": "9,833,517 sq km"},
                    "note": "includes only the 50 states",
                },
            },
            "People and Society": {
                "Population": {"total": {"text": "338 million"}},
                "0-14 years": {"text": "18%"},
            },
        }
    )


class TestAttributeAccess:
    def test_normalized_key(self, sample: FactbookDict) -> None:
        geo = sample.geography
        assert isinstance(geo, FactbookDict)

    def test_nested_attribute(self, sample: FactbookDict) -> None:
        assert sample.geography.location.text == "North America"

    def test_spaces_normalized(self, sample: FactbookDict) -> None:
        ps = sample.people_and_society
        assert isinstance(ps, FactbookDict)

    def test_digit_prefix(self, sample: FactbookDict) -> None:
        assert sample.people_and_society._0_14_years.text == "18%"

    def test_trailing_whitespace_key(self, sample: FactbookDict) -> None:
        assert sample.geography.area.total.text == "9,833,517 sq km"

    def test_missing_raises_attribute_error(self, sample: FactbookDict) -> None:
        with pytest.raises(AttributeError, match="No key matching"):
            sample.nonexistent


class TestDictAccess:
    def test_original_key(self, sample: FactbookDict) -> None:
        assert sample["Geography"]["Location"]["text"] == "North America"

    def test_case_insensitive(self, sample: FactbookDict) -> None:
        assert sample["geography"]["Location"]["text"] == "North America"

    def test_original_with_spaces(self, sample: FactbookDict) -> None:
        assert sample["People and Society"]["Population"]["total"]["text"] == "338 million"

    def test_missing_raises_key_error(self, sample: FactbookDict) -> None:
        with pytest.raises(KeyError):
            sample["nope"]


class TestContains:
    def test_exact(self, sample: FactbookDict) -> None:
        assert "Geography" in sample

    def test_normalized(self, sample: FactbookDict) -> None:
        assert "geography" in sample

    def test_missing(self, sample: FactbookDict) -> None:
        assert "nope" not in sample

    def test_non_string(self, sample: FactbookDict) -> None:
        assert 42 not in sample


class TestIterLen:
    def test_len(self, sample: FactbookDict) -> None:
        assert len(sample) == 2

    def test_iter(self, sample: FactbookDict) -> None:
        assert list(sample) == ["Geography", "People and Society"]


class TestReprStr:
    def test_repr_short(self, sample: FactbookDict) -> None:
        r = repr(sample)
        assert "FactbookDict" in r
        assert "Geography" in r

    def test_repr_long(self) -> None:
        d = FactbookDict({f"k{i}": i for i in range(10)})
        r = repr(d)
        assert "+5 more" in r

    def test_str_leaf_text_only(self) -> None:
        d = FactbookDict({"text": "hello"})
        assert str(d) == "hello"

    def test_str_leaf_text_and_note(self) -> None:
        d = FactbookDict({"text": "hello", "note": "a note"})
        assert str(d) == "hello"

    def test_str_non_leaf(self, sample: FactbookDict) -> None:
        assert str(sample) == repr(sample)


class TestReadOnly:
    def test_setattr_raises(self, sample: FactbookDict) -> None:
        with pytest.raises(AttributeError, match="read-only"):
            sample.geography = "nope"


class TestDir:
    def test_dir_returns_normalized(self, sample: FactbookDict) -> None:
        d = dir(sample)
        assert "geography" in d
        assert "people_and_society" in d


class TestMethods:
    def test_keys(self, sample: FactbookDict) -> None:
        assert list(sample.keys()) == ["Geography", "People and Society"]

    def test_values(self, sample: FactbookDict) -> None:
        vals = sample.values()
        assert len(vals) == 2
        assert all(isinstance(v, FactbookDict) for v in vals)

    def test_items(self, sample: FactbookDict) -> None:
        items = sample.items()
        assert len(items) == 2
        assert items[0][0] == "Geography"
        assert isinstance(items[0][1], FactbookDict)

    def test_to_dict(self, sample: FactbookDict) -> None:
        d = sample.to_dict()
        assert isinstance(d, dict)
        assert "Geography" in d
