from __future__ import annotations

import re
from typing import Any, Iterator


def _normalize_key(key: str) -> str:
    """Normalize a JSON key to a valid Python identifier.

    Examples:
        'People and Society' -> 'people_and_society'
        'Area - comparative' -> 'area_comparative'
        'freshwater lake(s)' -> 'freshwater_lake_s'
        'GDP - composition, by sector' -> 'gdp_composition_by_sector'
        '0-14 years' -> '_0_14_years'
    """
    s = key.strip().lower()
    s = s.replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = s.strip("_")
    if s and s[0].isdigit():
        s = "_" + s
    return s


class FactbookDict:
    """A read-only, recursively-wrapped dictionary that supports both
    attribute access and dictionary access with case-insensitive key lookup.

    Attribute access uses normalized keys::

        us.people_and_society.population.total.text

    Dictionary access uses original keys (case-insensitive)::

        us["People and Society"]["Population"]["total"]["text"]
    """

    __slots__ = ("_data", "_norm_map")

    def __init__(self, data: dict[str, Any]) -> None:
        object.__setattr__(self, "_data", data)
        norm_map: dict[str, str] = {}
        for key in data:
            norm = _normalize_key(key)
            norm_map[norm] = key
            lower = key.strip().lower()
            if lower not in norm_map:
                norm_map[lower] = key
        object.__setattr__(self, "_norm_map", norm_map)

    def _resolve_key(self, key: str) -> str | None:
        """Resolve a key to its original form.

        Tries: exact match, then normalized match, then case-insensitive match.
        """
        if key in self._data:
            return key
        norm = _normalize_key(key)
        if norm in self._norm_map:
            return self._norm_map[norm]
        return None

    def _wrap(self, value: Any) -> Any:
        """Recursively wrap dict values into FactbookDict."""
        if isinstance(value, dict):
            return FactbookDict(value)
        return value

    def __getattr__(self, name: str) -> Any:
        if name.startswith("__"):
            raise AttributeError(name)
        resolved = self._resolve_key(name)
        if resolved is not None:
            return self._wrap(self._data[resolved])
        raise AttributeError(
            f"No key matching '{name}'. "
            f"Available: {', '.join(self._data.keys())}"
        )

    def __getitem__(self, key: str) -> Any:
        resolved = self._resolve_key(key)
        if resolved is not None:
            return self._wrap(self._data[resolved])
        raise KeyError(key)

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, str):
            return False
        return self._resolve_key(key) is not None

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        keys = list(self._data.keys())
        if len(keys) <= 5:
            return f"FactbookDict({keys})"
        return f"FactbookDict({keys[:5]} ... +{len(keys) - 5} more)"

    def __str__(self) -> str:
        data_keys = set(self._data.keys())
        if data_keys == {"text"}:
            return str(self._data["text"])
        if data_keys == {"text", "note"}:
            return str(self._data["text"])
        return repr(self)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("FactbookDict is read-only")

    def __dir__(self) -> list[str]:
        """Enable tab completion in IPython/Jupyter."""
        normalized = [_normalize_key(k) for k in self._data]
        return sorted(set(normalized))

    def keys(self) -> dict[str, Any].keys:  # type: ignore[type-arg]
        """Return original (un-normalized) keys."""
        return self._data.keys()

    def values(self):  # type: ignore[override]
        """Return wrapped values."""
        return [self._wrap(v) for v in self._data.values()]

    def items(self):  # type: ignore[override]
        """Return (original_key, wrapped_value) pairs."""
        return [(k, self._wrap(v)) for k, v in self._data.items()]

    def to_dict(self) -> dict[str, Any]:
        """Return the underlying raw dictionary (not wrapped)."""
        return self._data
