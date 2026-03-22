#!/usr/bin/env python3
"""Generate the COUNTRY_REGISTRY dict for _loader.py.

Scans all data/{region}/*.json files, extracts country names from the JSON,
and outputs a Python dict literal to stdout.
"""

import json
import re
from pathlib import Path

DATA_DIR = Path("src/cia_world_factbook/data")

# Manual aliases for major countries
MANUAL_ALIASES = {
    "usa": ("north-america", "us"),
    "united_states": ("north-america", "us"),
    "united_states_of_america": ("north-america", "us"),
    "america": ("north-america", "us"),
    "great_britain": ("europe", "uk"),
    "england": ("europe", "uk"),
    "china": ("east-n-southeast-asia", "ch"),
    "peoples_republic_of_china": ("east-n-southeast-asia", "ch"),
    "south_korea": ("east-n-southeast-asia", "ks"),
    "north_korea": ("east-n-southeast-asia", "kn"),
    "russia": ("europe", "rs"),
    "uae": ("middle-east", "ae"),
    "ivory_coast": ("africa", "iv"),
}


def normalize_name(name: str) -> str:
    """Normalize a country name to a valid Python identifier."""
    s = name.strip().lower()
    s = s.replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = s.strip("_")
    if s and s[0].isdigit():
        s = "_" + s
    return s


def extract_country_name(data: dict) -> str | None:
    """Extract the conventional short form country name from JSON data."""
    try:
        gov = data.get("Government", {})
        cn = gov.get("Country name", {})
        short = cn.get("conventional short form", {})
        text = short.get("text", "")
        if text and text.lower() != "none":
            return text
    except (AttributeError, TypeError):
        pass
    return None


def main():
    entries: dict[str, tuple[str, str]] = {}

    for region_dir in sorted(DATA_DIR.iterdir()):
        if not region_dir.is_dir():
            continue
        region = region_dir.name
        for json_file in sorted(region_dir.glob("[a-z][a-z].json")):
            code = json_file.stem
            entry = (region, code)

            # Primary entry: 2-letter code
            entries[code] = entry

            # Extract friendly name
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            name = extract_country_name(data)
            if name:
                normalized = normalize_name(name)
                if normalized and normalized not in entries:
                    entries[normalized] = entry

    # Add manual aliases (don't overwrite existing)
    for alias, entry in MANUAL_ALIASES.items():
        if alias not in entries:
            entries[alias] = entry

    # Output the dict
    print("COUNTRY_REGISTRY: dict[str, tuple[str, str]] = {")

    # Group by region for readability
    by_region: dict[str, list[tuple[str, tuple[str, str]]]] = {}
    for key, (region, code) in sorted(entries.items(), key=lambda x: (x[1][0], x[1][1], x[0])):
        by_region.setdefault(region, []).append((key, (region, code)))

    for region in sorted(by_region.keys()):
        print(f"    # {region}")
        for key, (r, c) in by_region[region]:
            print(f'    "{key}": ("{r}", "{c}"),')
        print()

    print("}")
    print(f"\n# Total entries: {len(entries)}")


if __name__ == "__main__":
    main()
