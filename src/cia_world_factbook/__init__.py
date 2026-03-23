"""CIA World Factbook data as a Python package.

Usage::

    from cia_world_factbook import us

    # Attribute access (normalized keys)
    us.geography.location.text
    us.people_and_society.population.total.text

    # Dictionary access (original keys, case-insensitive)
    us["Geography"]["Location"]["text"]
    us["People and Society"]["Population"]["total"]["text"]
"""

from __future__ import annotations

__version__ = "0.1.0"


def __getattr__(name: str):
    """Module-level lazy loading of country data.

    Enables: ``from cia_world_factbook import us``
    """
    from ._loader import COUNTRY_REGISTRY, load_country

    if name in COUNTRY_REGISTRY:
        country = load_country(name)
        globals()[name] = country
        return country

    raise AttributeError(f"module 'cia_world_factbook' has no attribute '{name}'")


def __dir__():
    """Support tab completion at the module level."""
    from ._loader import COUNTRY_REGISTRY

    return sorted(set(list(COUNTRY_REGISTRY.keys()) + ["__version__", "load_country", "compare"]))


def load_country(name: str):
    """Explicitly load a country by name.

    Args:
        name: Country identifier (e.g., 'us', 'usa', 'united_states')

    Returns:
        FactbookDict wrapping the country's data.
    """
    from ._loader import load_country as _load

    return _load(name)


def list_countries() -> list[str]:
    """Return sorted list of all 2-letter country codes."""
    from ._loader import COUNTRY_REGISTRY

    return sorted({code for code, (_, stem) in COUNTRY_REGISTRY.items() if code == stem})


def list_regions() -> list[str]:
    """Return sorted list of all region names."""
    from ._loader import COUNTRY_REGISTRY

    return sorted({region for region, _ in COUNTRY_REGISTRY.values()})


def search(query: str) -> list[tuple[str, str, str]]:
    """Search for countries by name or code.

    Args:
        query: Search term (case-insensitive). Matches against codes
               and friendly names.

    Returns:
        List of (code, friendly_name, region) tuples for matches.
    """
    from ._loader import COUNTRY_REGISTRY

    query_lower = query.lower()
    # Build code -> (friendly_names, region) mapping
    code_info: dict[str, tuple[list[str], str]] = {}
    for key, (region, code) in COUNTRY_REGISTRY.items():
        if code not in code_info:
            code_info[code] = ([], region)
        if key != code:
            code_info[code][0].append(key)

    results = []
    for code, (names, region) in sorted(code_info.items()):
        searchable = [code] + names
        if any(query_lower in s for s in searchable):
            best_name = max(names, key=len) if names else code
            results.append((code, best_name, region))
    return results


def compare(path: str) -> dict:
    """Get a single metric across all 256 countries.

    Args:
        path: Dot-separated attribute path using normalized keys.
              Example: ``"economy.gdp_official_exchange_rate"``

    Returns:
        Dict mapping 2-letter country codes to the value at that path,
        or ``None`` if the country lacks the given field.
    """
    from ._loader import compare as _compare

    return _compare(path)


def info() -> str:
    """Print a reference table of all available countries.

    Returns:
        Formatted table string (also printed to stdout).
    """
    from ._loader import COUNTRY_REGISTRY

    # Build code -> (names, region)
    code_info: dict[str, tuple[list[str], str]] = {}
    for key, (region, code) in COUNTRY_REGISTRY.items():
        if code not in code_info:
            code_info[code] = ([], region)
        if key != code:
            code_info[code][0].append(key)

    lines = []
    lines.append(f"{'Code':<6} {'Name':<45} {'Region'}")
    lines.append("-" * 85)

    by_region: dict[str, list[tuple[str, str]]] = {}
    for code, (names, region) in sorted(code_info.items()):
        best_name = max(names, key=len) if names else code
        by_region.setdefault(region, []).append((code, best_name))

    for region in sorted(by_region.keys()):
        for code, name in sorted(by_region[region], key=lambda x: x[1]):
            lines.append(f"{code:<6} {name:<45} {region}")

    table = "\n".join(lines)
    print(table)
    return table
