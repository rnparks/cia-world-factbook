"""Performance tests to measure query latency and identify bottlenecks.

These tests measure actual timing to help decide if Python is sufficient
or if performance-critical paths need optimization (e.g., Rust extension).
"""

import time

import pytest

from cia_world_factbook._loader import load_country, _country_cache, COUNTRY_REGISTRY
from cia_world_factbook._wrapper import FactbookDict


class TestFirstLoadPerformance:
    """Measure cold-start loading time (JSON parse + FactbookDict creation)."""

    def test_first_load_under_100ms(self) -> None:
        """A single country should load in well under 100ms."""
        # Clear cache to force cold load
        _country_cache.pop("mx", None)
        start = time.perf_counter()
        load_country("mx")
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"\n  First load (Mexico): {elapsed_ms:.2f}ms")
        assert elapsed_ms < 100, f"First load took {elapsed_ms:.2f}ms (limit: 100ms)"

    def test_cached_load_under_1ms(self) -> None:
        """Cached load should be essentially free."""
        load_country("us")  # ensure cached
        start = time.perf_counter()
        for _ in range(1000):
            load_country("us")
        elapsed_ms = (time.perf_counter() - start) * 1000
        per_call = elapsed_ms / 1000
        print(f"\n  Cached load: {per_call:.4f}ms per call")
        assert per_call < 0.1, f"Cached load took {per_call:.4f}ms (limit: 0.1ms)"


class TestAttributeAccessPerformance:
    """Measure attribute traversal latency."""

    def test_single_traversal_under_1ms(self) -> None:
        """A 4-level traversal should be under 1ms."""
        us = load_country("us")
        start = time.perf_counter()
        for _ in range(1000):
            _ = us.geography.location.text
        elapsed_ms = (time.perf_counter() - start) * 1000
        per_call = elapsed_ms / 1000
        print(f"\n  Attribute traversal (4 levels): {per_call:.4f}ms per call")
        assert per_call < 1.0, f"Traversal took {per_call:.4f}ms (limit: 1.0ms)"

    def test_dict_access_under_1ms(self) -> None:
        """Dictionary access should be comparable to attribute access."""
        us = load_country("us")
        start = time.perf_counter()
        for _ in range(1000):
            _ = us["Geography"]["Location"]["text"]
        elapsed_ms = (time.perf_counter() - start) * 1000
        per_call = elapsed_ms / 1000
        print(f"\n  Dict access (3 levels): {per_call:.4f}ms per call")
        assert per_call < 1.0, f"Dict access took {per_call:.4f}ms (limit: 1.0ms)"

    def test_normalized_key_resolution_under_1ms(self) -> None:
        """Normalized key resolution (people_and_society) should be fast."""
        us = load_country("us")
        start = time.perf_counter()
        for _ in range(1000):
            _ = us.people_and_society.population.total.text
        elapsed_ms = (time.perf_counter() - start) * 1000
        per_call = elapsed_ms / 1000
        print(f"\n  Normalized key traversal (4 levels): {per_call:.4f}ms per call")
        assert per_call < 1.0, f"Normalized traversal took {per_call:.4f}ms (limit: 1.0ms)"


class TestBulkLoadPerformance:
    """Measure loading many countries at once."""

    def test_load_10_countries_under_500ms(self) -> None:
        """Loading 10 countries cold should be under 500ms."""
        codes = ["fr", "gm", "ja", "br", "eg", "ke", "ar", "pk", "th", "pl"]
        for c in codes:
            _country_cache.pop(c, None)

        start = time.perf_counter()
        for code in codes:
            load_country(code)
        elapsed_ms = (time.perf_counter() - start) * 1000
        per_country = elapsed_ms / len(codes)
        print(f"\n  Load 10 countries: {elapsed_ms:.2f}ms total, {per_country:.2f}ms each")
        assert elapsed_ms < 500, f"Bulk load took {elapsed_ms:.2f}ms (limit: 500ms)"

    def test_load_all_countries_under_10s(self) -> None:
        """Loading ALL 256 countries should be under 10 seconds."""
        _country_cache.clear()
        codes = sorted({code for code, (_, stem) in COUNTRY_REGISTRY.items() if code == stem})

        start = time.perf_counter()
        for code in codes:
            load_country(code)
        elapsed_ms = (time.perf_counter() - start) * 1000
        per_country = elapsed_ms / len(codes)
        print(f"\n  Load all {len(codes)} countries: {elapsed_ms:.0f}ms total, {per_country:.2f}ms each")
        assert elapsed_ms < 10000, f"Loading all countries took {elapsed_ms:.0f}ms (limit: 10s)"


class TestQueryPerformance:
    """Measure realistic query patterns."""

    def test_1000_random_queries_under_1s(self) -> None:
        """1000 attribute accesses across different countries."""
        countries = [load_country(c) for c in ["us", "ca", "gm", "ja", "br"]]

        start = time.perf_counter()
        for i in range(1000):
            c = countries[i % len(countries)]
            _ = c.geography.location.text
        elapsed_ms = (time.perf_counter() - start) * 1000
        per_query = elapsed_ms / 1000
        print(f"\n  1000 queries across 5 countries: {elapsed_ms:.2f}ms total, {per_query:.4f}ms each")
        assert elapsed_ms < 1000, f"1000 queries took {elapsed_ms:.2f}ms (limit: 1000ms)"

    def test_iteration_performance(self) -> None:
        """Iterating all keys and accessing values."""
        us = load_country("us")
        start = time.perf_counter()
        for _ in range(100):
            for key in us:
                _ = us[key]
        elapsed_ms = (time.perf_counter() - start) * 1000
        per_iter = elapsed_ms / 100
        print(f"\n  Full iteration (13 sections): {per_iter:.4f}ms per iteration")
        assert per_iter < 5.0, f"Iteration took {per_iter:.4f}ms (limit: 5.0ms)"

    def test_dir_performance(self) -> None:
        """dir() for tab completion should be fast."""
        us = load_country("us")
        start = time.perf_counter()
        for _ in range(10000):
            _ = dir(us)
        elapsed_ms = (time.perf_counter() - start) * 1000
        per_call = elapsed_ms / 10000
        print(f"\n  dir() call: {per_call:.4f}ms per call")
        assert per_call < 0.5, f"dir() took {per_call:.4f}ms (limit: 0.5ms)"

    def test_str_on_leaf_performance(self) -> None:
        """str() on a leaf node."""
        us = load_country("us")
        leaf = us.geography.location
        start = time.perf_counter()
        for _ in range(10000):
            _ = str(leaf)
        elapsed_ms = (time.perf_counter() - start) * 1000
        per_call = elapsed_ms / 10000
        print(f"\n  str(leaf): {per_call:.4f}ms per call")
        assert per_call < 0.1, f"str(leaf) took {per_call:.4f}ms (limit: 0.1ms)"


class TestMemoryFootprint:
    """Basic memory usage tests."""

    def test_wrapper_size_reasonable(self) -> None:
        """A single FactbookDict should not use excessive memory."""
        import sys
        us = load_country("us")
        # Shallow size (just the wrapper object, not the data)
        size = sys.getsizeof(us)
        print(f"\n  FactbookDict shallow size: {size} bytes")
        # The wrapper itself should be small (slots-based)
        assert size < 200, f"Wrapper size {size} bytes seems too large"
