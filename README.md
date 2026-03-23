# cia-world-factbook

[![CI](https://github.com/rnparks/cia-world-factbook/actions/workflows/ci.yml/badge.svg)](https://github.com/rnparks/cia-world-factbook/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/cia-world-factbook)](https://pypi.org/project/cia-world-factbook/)

Pythonic access to CIA World Factbook data for 256 countries and territories across 12 regions. Zero dependencies. Supports both attribute access (dot notation) and dictionary access with case-insensitive key lookup, tab completion, and built-in search.

## Installation

```bash
pip install cia-world-factbook
```

Or with uv:

```bash
uv add cia-world-factbook
```

No external dependencies -- uses only the Python standard library.

## Quick Start

```python
from cia_world_factbook import us

us.geography.location.text
# 'North America, bordering both the North Atlantic Ocean and the North Pacific Ocean, between Canada and Mexico'

us.people_and_society.population.total.text
# '338,016,259 (2025 est.)'

us.government.capital.name.text
# 'Washington, DC'

us.economy.gdp_official_exchange_rate.text
# '$28.78 trillion (2024 est.)'
```

---

## Two Ways to Access Data

Every piece of data supports both dot notation and bracket notation. You can mix them freely.

### Attribute access (dot notation)

Keys are normalized to valid Python identifiers: lowercased, spaces/punctuation become underscores.

```python
from cia_world_factbook import us

us.geography.location.text
us.people_and_society.population.total.text
us.economy.gdp_official_exchange_rate.text
```

### Dictionary access (bracket notation)

Uses the original CIA Factbook key names. Case-insensitive.

```python
us["Geography"]["Location"]["text"]
us["People and Society"]["Population"]["total"]["text"]
us["Economy"]["GDP (official exchange rate)"]["text"]
```

### Mixed access

Combine both styles in the same expression:

```python
us.government["Capital"]["name"].text
us["Geography"].location.text
```

### Key normalization rules

| Original Key | Normalized | Rule |
|---|---|---|
| `People and Society` | `people_and_society` | spaces to underscores |
| `Area - comparative` | `area_comparative` | hyphens/spaces to underscores |
| `freshwater lake(s)` | `freshwater_lake_s` | parentheses removed |
| `GDP - composition, by sector` | `gdp_composition_by_sector` | punctuation removed |
| `0-14 years` | `_0_14_years` | leading digit gets `_` prefix |
| `Military & Security` | `military_and_security` | `&` becomes `and` |

### How key lookup works

When you access a key, the package tries three strategies in order:

1. **Exact match** -- `us["Geography"]` finds `"Geography"` directly
2. **Normalized match** -- `us.geography` normalizes to `"geography"`, maps to `"Geography"`
3. **Case-insensitive match** -- `us["geography"]` matches `"Geography"` via lowercase comparison

This means `us["Geography"]`, `us["geography"]`, and `us.geography` all return the same data.

---

## Loading Countries

### Import directly

```python
from cia_world_factbook import us, ca, gm, ja, br, fr
```

Countries are **lazy-loaded** -- no JSON is parsed until you first access a country. Subsequent accesses use a cache and are essentially free.

### Load by name or code

```python
from cia_world_factbook import load_country

# By 2-letter CIA code
us = load_country("us")
ja = load_country("ja")

# By friendly name
germany = load_country("germany")
australia = load_country("australia")

# By alias
usa = load_country("usa")
uk = load_country("united_kingdom")
```

### Python keyword codes

The codes `as` (Australia), `in` (India), and `is` (Israel) are Python keywords and cannot be used with `from ... import`. Use `load_country()` or the friendly name instead:

```python
# These WON'T work:
# from cia_world_factbook import as   # SyntaxError
# from cia_world_factbook import in   # SyntaxError

# These WILL work:
from cia_world_factbook import load_country
australia = load_country("as")        # by code
australia = load_country("australia")  # by name

from cia_world_factbook import australia  # by friendly name import
```

### Caching

Each country's JSON is parsed only once. All aliases for the same country share the same underlying data:

```python
us1 = load_country("us")
us2 = load_country("usa")
us3 = load_country("united_states")
# us1.to_dict() == us2.to_dict() == us3.to_dict()
```

---

## Discovering and Searching Countries

### `search(query)` -- find countries by partial match

Searches country codes, friendly names, and aliases. Case-insensitive.

```python
import cia_world_factbook

cia_world_factbook.search("korea")
# [('kn', 'north_korea', 'east-n-southeast-asia'),
#  ('ks', 'south_korea', 'east-n-southeast-asia')]

cia_world_factbook.search("island")
# [('at', 'ashmore_and_cartier_islands', 'australia-oceania'),
#  ('bp', 'solomon_islands', 'australia-oceania'),
#  ('bq', 'navassa_island', 'central-america-n-caribbean'),
#  ...]

cia_world_factbook.search("stan")
# [('af', 'afghanistan', 'south-asia'),
#  ('kg', 'kyrgyzstan', 'central-asia'),
#  ('kz', 'kazakhstan', 'central-asia'),
#  ('pk', 'pakistan', 'south-asia'),
#  ('ti', 'tajikistan', 'central-asia'),
#  ('tx', 'turkmenistan', 'central-asia'),
#  ('uz', 'uzbekistan', 'central-asia')]
```

Returns a list of `(code, friendly_name, region)` tuples.

### `info()` -- print a full reference table

Prints a formatted table of all 256 countries to stdout, and also returns it as a string.

```python
import cia_world_factbook

cia_world_factbook.info()
# Code   Name                                          Region
# ---------------------------------------------------------------------------
# ag     algeria                                       africa
# ao     angola                                        africa
# bn     benin                                         africa
# ...    ...                                           ...
```

### `list_countries()` -- all 2-letter codes

```python
from cia_world_factbook import list_countries

codes = list_countries()
# ['aa', 'ac', 'ae', 'af', 'ag', ..., 'zi']
len(codes)
# 256
```

### `list_regions()` -- all 12 region names

```python
from cia_world_factbook import list_regions

list_regions()
# ['africa', 'antarctica', 'australia-oceania', 'central-america-n-caribbean',
#  'central-asia', 'east-n-southeast-asia', 'europe', 'middle-east',
#  'north-america', 'south-america', 'south-asia', 'world']
```

---

## Comparing Countries

### `compare(path)` -- get one metric across all 256 countries

Pass a dot-separated path using normalized keys. Returns a dict mapping country codes to values, or `None` for countries that lack the field.

```python
from cia_world_factbook import compare

compare("economy.gdp_official_exchange_rate")
# {'us': '$29.185 trillion (2024 est.)', 'fr': '$3.162 trillion (2024 est.)', 'ay': None, ...}

compare("government.capital.name")
# {'us': 'Washington, DC', 'fr': 'Paris', 'ja': 'Tokyo', ...}

compare("people_and_society.population.total")
# {'us': '338,016,259 (2025 est.)', 'ch': '1,416,043,270 (2025 est.)', ...}
```

Works with any path you can use in dot notation on a single country. Countries missing the field return `None` (e.g., Antarctica has no GDP).

---

## Exploring Country Data

### Data sections

Each country has up to 13 top-level sections:

```python
from cia_world_factbook import us

list(us.keys())
# ['Introduction', 'Geography', 'People and Society', 'Environment',
#  'Government', 'Economy', 'Energy', 'Communications', 'Transportation',
#  'Military and Security', 'Space', 'Terrorism', 'Transnational Issues']
```

Not every country has all sections. Small territories may only have a few.

### Drilling into a section

```python
list(us.geography.keys())
# ['Location', 'Geographic coordinates', 'Map references', 'Area',
#  'Area - comparative', 'Land boundaries', 'Coastline', 'Maritime claims',
#  'Climate', 'Terrain', 'Elevation', 'Natural resources', 'Land use',
#  'Irrigated land', 'Major lakes (area sq km)', 'Major rivers (by length in km)',
#  'Major watersheds (area sq km)', 'Population distribution',
#  'Natural hazards', 'Geography - note']
```

### `len()` -- how many keys at any level

```python
len(us)                # 13 top-level sections
len(us.geography)      # 20 geography fields
len(us.economy)        # number of economy fields
```

### `in` operator -- check if a key exists

Works with both original and normalized key names:

```python
"Geography" in us           # True
"geography" in us           # True (case-insensitive)
"people_and_society" in us  # True (normalized)
"Nonexistent" in us         # False
```

### Iteration -- loop over keys

```python
for section in us:
    print(section)
# Introduction
# Geography
# People and Society
# ...

for key, value in us.geography.items():
    print(f"{key}: {type(value)}")
# Location: <class 'cia_world_factbook._wrapper.FactbookDict'>
# Geographic coordinates: <class 'cia_world_factbook._wrapper.FactbookDict'>
# ...
```

### `keys()`, `values()`, `items()`

These work like standard dict methods. `keys()` returns the **original** (un-normalized) key names:

```python
us.keys()     # dict_keys(['Introduction', 'Geography', 'People and Society', ...])
us.values()   # [FactbookDict(...), FactbookDict(...), ...]
us.items()    # [('Introduction', FactbookDict(...)), ('Geography', FactbookDict(...)), ...]
```

### `to_dict()` -- get the raw underlying dict

Returns the original Python dictionary (not wrapped). Useful for serialization or passing to other libraries:

```python
raw = us.geography.area.to_dict()
# {'total ': {'text': '9,833,517 sq km'}, 'land': {'text': '9,147,593 sq km'}, ...}

import json
json.dumps(raw, indent=2)
```

---

## String Behavior

### `str()` on leaf nodes returns the text directly

When a node contains only a `text` field (or `text` + `note`), `str()` returns just the text value. This makes `print()` work naturally:

```python
print(us.geography.location)
# North America, bordering both the North Atlantic Ocean and the North Pacific Ocean, between Canada and Mexico

# Equivalent to:
print(us.geography.location.text)
```

### `str()` on non-leaf nodes returns a summary

```python
str(us.geography)
# "FactbookDict(['Location', 'Geographic coordinates', 'Map references', 'Area', 'Area - comparative'] ... +15 more)"
```

### `repr()` shows available keys

Useful in the REPL for seeing what's inside a node:

```python
>>> us.geography
FactbookDict(['Location', 'Geographic coordinates', 'Map references', 'Area', 'Area - comparative'] ... +15 more)

>>> us.geography.area
FactbookDict(['total ', 'land', 'water'])
```

---

## Tab Completion (IPython / Jupyter)

`dir()` on any node returns normalized key names, which powers tab completion:

```python
dir(us)
# ['communications', 'economy', 'energy', 'environment', 'geography',
#  'government', 'introduction', 'military_and_security',
#  'people_and_society', 'space', 'terrorism', 'transnational_issues',
#  'transportation']

dir(us.geography)
# ['area', 'area_comparative', 'climate', 'coastline', 'elevation', ...]
```

In IPython or Jupyter:

```
In [1]: from cia_world_factbook import us
In [2]: us.geo<TAB>        # completes to us.geography
In [3]: us.geography.loc<TAB>  # completes to us.geography.location
```

Tab completion also works at the module level:

```
In [1]: import cia_world_factbook
In [2]: cia_world_factbook.aus<TAB>  # completes to cia_world_factbook.australia
```

---

## Read-Only Data

All data is read-only. Attempting to modify any value raises an error:

```python
us.geography = "nope"
# AttributeError: FactbookDict is read-only
```

## Error Messages

Missing keys produce helpful error messages that list what's available:

```python
us.geograpy  # typo
# AttributeError: No key matching 'geograpy'. Available: Introduction, Geography, People and Society, ...

load_country("atlantis")
# ValueError: Unknown country 'atlantis'. Available: aa, ac, ae, af, ...
```

---

## Performance

All data is bundled as JSON and loaded lazily. No database, no network calls, no external dependencies.

| Operation | Time |
|---|---|
| First load (single country, cold) | ~1ms |
| Cached load (subsequent access) | ~0.0001ms |
| Attribute traversal (4 levels deep) | ~0.04ms |
| Load ALL 256 countries | ~120ms |
| 1,000 queries across 5 countries | ~43ms |
| FactbookDict wrapper memory | 48 bytes |

Python is more than fast enough -- no native extensions needed.

---

## Version

```python
import cia_world_factbook
cia_world_factbook.__version__
# '0.1.1'
```

---

## Complete API Reference

### Module-level functions

| Function | Description |
|---|---|
| `load_country(name)` | Load a country by 2-letter code, friendly name, or alias. Returns a `FactbookDict`. |
| `search(query)` | Search countries by partial match. Returns `list[tuple[code, name, region]]`. |
| `info()` | Print a reference table of all countries. Also returns the table as a string. |
| `list_countries()` | Return sorted list of all 256 two-letter country codes. |
| `list_regions()` | Return sorted list of all 12 region names. |
| `compare(path)` | Get a single metric across all 256 countries. Returns `dict[str, str \| None]`. |

### Module-level attributes

| Attribute | Description |
|---|---|
| `__version__` | Package version string (e.g., `'0.1.1'`). |
| `us`, `ca`, `gm`, ... | Lazy-loaded country data. Any registry key works as an import or attribute. |

### `FactbookDict` -- the data wrapper

Every country and every nested node is a `FactbookDict`. It supports:

| Feature | Example | Description |
|---|---|---|
| Attribute access | `us.geography` | Normalized key lookup with dot notation |
| Dictionary access | `us["Geography"]` | Original or normalized key, case-insensitive |
| `str()` | `str(us.geography.location)` | Returns text value for leaf nodes, repr for branches |
| `repr()` | `repr(us.geography)` | Shows first 5 keys and count of remaining |
| `len()` | `len(us)` | Number of keys at this level |
| `in` | `"geography" in us` | Check if a key exists (case-insensitive) |
| `for key in obj` | `for k in us: ...` | Iterate over original key names |
| `dir()` | `dir(us)` | Normalized keys for tab completion |
| `keys()` | `us.keys()` | Original key names (`dict_keys`) |
| `values()` | `us.values()` | List of wrapped child values |
| `items()` | `us.items()` | List of `(original_key, wrapped_value)` pairs |
| `to_dict()` | `us.to_dict()` | Raw Python dict (unwrapped) |
| Read-only | `us.x = 1` raises | All data is immutable |

---

## Data Source

Country data is sourced from [factbook.json](https://github.com/taruen/factbook.json), a JSON extraction of the [CIA World Factbook](https://www.cia.gov/the-world-factbook/).

---

## Country Reference

256 countries and territories across 12 regions. Use `search()` or `info()` to explore interactively, or expand a region below.

<details>
<summary>Africa (56)</summary>

| Code | Name | Aliases |
|------|------|---------|
| `ag` | algeria | |
| `ao` | angola | |
| `bn` | benin | |
| `bc` | botswana | |
| `uv` | burkina_faso | |
| `by` | burundi | |
| `cv` | cabo_verde | |
| `cm` | cameroon | |
| `ct` | central_african_republic | |
| `cd` | chad | |
| `cn` | comoros | |
| `cg` | congo_democratic_republic | |
| `cf` | congo_republic | |
| `iv` | cote_d_ivoire | ivory_coast |
| `dj` | djibouti | |
| `eg` | egypt | |
| `ek` | equatorial_guinea | |
| `er` | eritrea | |
| `wz` | eswatini | |
| `et` | ethiopia | |
| `gb` | gabon | |
| `ga` | the_gambia | |
| `gh` | ghana | |
| `gv` | guinea | |
| `pu` | guinea_bissau | |
| `ke` | kenya | |
| `lt` | lesotho | |
| `li` | liberia | |
| `ly` | libya | |
| `ma` | madagascar | |
| `mi` | malawi | |
| `ml` | mali | |
| `mr` | mauritania | |
| `mp` | mauritius | |
| `mo` | morocco | |
| `mz` | mozambique | |
| `wa` | namibia | |
| `ng` | niger | |
| `ni` | nigeria | |
| `rw` | rwanda | |
| `sh` | saint_helena | |
| `tp` | sao_tome_and_principe | |
| `sg` | senegal | |
| `se` | seychelles | |
| `sl` | sierra_leone | |
| `so` | somalia | |
| `sf` | south_africa | |
| `od` | south_sudan | |
| `su` | sudan | |
| `tz` | tanzania | |
| `to` | togo | |
| `ts` | tunisia | |
| `ug` | uganda | |
| `wi` | western_sahara | |
| `za` | zambia | |
| `zi` | zimbabwe | |

</details>

<details>
<summary>Antarctica (4)</summary>

| Code | Name |
|------|------|
| `ay` | antarctica |
| `bv` | bouvet_island |
| `fs` | french_southern_and_antarctic_lands |
| `hm` | heard_island_and_mcdonald_islands |

</details>

<details>
<summary>Australia & Oceania (30)</summary>

| Code | Name |
|------|------|
| `aq` | american_samoa |
| `as` | australia |
| `at` | ashmore_and_cartier_islands |
| `bp` | solomon_islands |
| `ck` | cocos_keeling_islands |
| `cq` | northern_mariana_islands |
| `cr` | coral_sea_islands |
| `cw` | cook_islands |
| `fj` | fiji |
| `fm` | micronesia |
| `fp` | french_polynesia |
| `gq` | guam |
| `kr` | kiribati |
| `kt` | christmas_island |
| `nc` | new_caledonia |
| `ne` | niue |
| `nf` | norfolk_island |
| `nh` | vanuatu |
| `nr` | nauru |
| `nz` | new_zealand |
| `pc` | pitcairn_islands |
| `ps` | palau |
| `rm` | marshall_islands |
| `tl` | tokelau |
| `tn` | tonga |
| `tv` | tuvalu |
| `um` | us_pacific_island_wildlife_refuges |
| `wf` | wallis_and_futuna |
| `wq` | wake_island |
| `ws` | samoa |

</details>

<details>
<summary>Central America & Caribbean (33)</summary>

| Code | Name |
|------|------|
| `aa` | aruba |
| `ac` | antigua_and_barbuda |
| `av` | anguilla |
| `bb` | barbados |
| `bf` | the_bahamas |
| `bh` | belize |
| `bq` | navassa_island |
| `cj` | cayman_islands |
| `cs` | costa_rica |
| `cu` | cuba |
| `do` | dominica |
| `dr` | dominican_republic |
| `es` | el_salvador |
| `gj` | grenada |
| `gt` | guatemala |
| `ha` | haiti |
| `ho` | honduras |
| `jm` | jamaica |
| `mh` | montserrat |
| `nn` | sint_maarten |
| `nu` | nicaragua |
| `pm` | panama |
| `rn` | saint_martin |
| `rq` | puerto_rico |
| `sc` | saint_kitts_and_nevis |
| `st` | saint_lucia |
| `tb` | saint_barthelemy |
| `td` | trinidad_and_tobago |
| `tk` | turks_and_caicos_islands |
| `uc` | curacao |
| `vc` | saint_vincent_and_the_grenadines |
| `vi` | british_virgin_islands |
| `vq` | virgin_islands |

</details>

<details>
<summary>Central Asia (6)</summary>

| Code | Name |
|------|------|
| `kg` | kyrgyzstan |
| `kz` | kazakhstan |
| `rs` | russia |
| `ti` | tajikistan |
| `tx` | turkmenistan |
| `uz` | uzbekistan |

</details>

<details>
<summary>East & Southeast Asia (22)</summary>

| Code | Name | Aliases |
|------|------|---------|
| `bm` | burma | myanmar |
| `bx` | brunei | |
| `cb` | cambodia | |
| `ch` | china | peoples_republic_of_china |
| `hk` | hong_kong | |
| `id` | indonesia | |
| `ja` | japan | |
| `kn` | north_korea | |
| `ks` | south_korea | |
| `la` | laos | |
| `mc` | macau | |
| `mg` | mongolia | |
| `my` | malaysia | |
| `pf` | paracel_islands | |
| `pg` | spratly_islands | |
| `pp` | papua_new_guinea | |
| `rp` | philippines | |
| `sn` | singapore | |
| `th` | thailand | |
| `tt` | timor_leste | |
| `tw` | taiwan | |
| `vm` | vietnam | |

</details>

<details>
<summary>Europe (55)</summary>

| Code | Name | Aliases |
|------|------|---------|
| `al` | albania | |
| `an` | andorra | |
| `au` | austria | |
| `ax` | akrotiri | |
| `be` | belgium | |
| `bk` | bosnia_and_herzegovina | |
| `bo` | belarus | |
| `bu` | bulgaria | |
| `cy` | cyprus | |
| `da` | denmark | |
| `dx` | dhekelia | |
| `ee` | european_union | |
| `ei` | ireland | |
| `en` | estonia | |
| `ez` | czechia | |
| `fi` | finland | |
| `fo` | faroe_islands | |
| `fr` | france | |
| `gi` | gibraltar | |
| `gk` | guernsey | |
| `gm` | germany | |
| `gr` | greece | |
| `hr` | croatia | |
| `hu` | hungary | |
| `ic` | iceland | |
| `im` | isle_of_man | |
| `it` | italy | |
| `je` | jersey | |
| `jn` | jan_mayen | |
| `kv` | kosovo | |
| `lg` | latvia | |
| `lh` | lithuania | |
| `lo` | slovakia | |
| `ls` | liechtenstein | |
| `lu` | luxembourg | |
| `md` | moldova | |
| `mj` | montenegro | |
| `mk` | north_macedonia | |
| `mn` | monaco | |
| `mt` | malta | |
| `nl` | netherlands | |
| `no` | norway | |
| `pl` | poland | |
| `po` | portugal | |
| `ri` | serbia | |
| `ro` | romania | |
| `si` | slovenia | |
| `sm` | san_marino | |
| `sp` | spain | |
| `sv` | svalbard | |
| `sw` | sweden | |
| `sz` | switzerland | |
| `uk` | united_kingdom | england, great_britain |
| `up` | ukraine | |
| `vt` | holy_see | vatican |

</details>

<details>
<summary>Middle East (19)</summary>

| Code | Name | Aliases |
|------|------|---------|
| `ae` | united_arab_emirates | uae |
| `aj` | azerbaijan | |
| `am` | armenia | |
| `ba` | bahrain | |
| `gg` | georgia | |
| `gz` | gaza_strip | |
| `ir` | iran | |
| `is` | israel | |
| `iz` | iraq | |
| `jo` | jordan | |
| `ku` | kuwait | |
| `le` | lebanon | |
| `mu` | oman | |
| `qa` | qatar | |
| `sa` | saudi_arabia | |
| `sy` | syria | |
| `tu` | turkey | |
| `we` | west_bank | |
| `ym` | yemen | |

</details>

<details>
<summary>North America (7)</summary>

| Code | Name | Aliases |
|------|------|---------|
| `bd` | bermuda | |
| `ca` | canada | |
| `gl` | greenland | |
| `ip` | clipperton_island | |
| `mx` | mexico | |
| `sb` | saint_pierre_and_miquelon | |
| `us` | united_states | usa, america, united_states_of_america |

</details>

<details>
<summary>South America (14)</summary>

| Code | Name |
|------|------|
| `ar` | argentina |
| `bl` | bolivia |
| `br` | brazil |
| `ci` | chile |
| `co` | colombia |
| `ec` | ecuador |
| `fk` | falkland_islands |
| `gy` | guyana |
| `ns` | suriname |
| `pa` | paraguay |
| `pe` | peru |
| `sx` | south_georgia_and_south_sandwich_islands |
| `uy` | uruguay |
| `ve` | venezuela |

</details>

<details>
<summary>South Asia (9)</summary>

| Code | Name |
|------|------|
| `af` | afghanistan |
| `bg` | bangladesh |
| `bt` | bhutan |
| `ce` | sri_lanka |
| `in` | india |
| `io` | british_indian_ocean_territory |
| `mv` | maldives |
| `np` | nepal |
| `pk` | pakistan |

</details>

<details>
<summary>World (1)</summary>

| Code | Name |
|------|------|
| `xx` | world |

</details>

## License

MIT
