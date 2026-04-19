import pytest
from dataclasses import dataclass, field
from typing import Optional
from pipecheck.rules.cache_rules import (
    NoCacheStrategyRule,
    InvalidCacheStrategyRule,
    CacheTTLTooLongRule,
    ZeroCacheTTLRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FakePipeline:
    cache_strategy: Optional[str] = None
    cache_ttl_hours: Optional[float] = None


# NoCacheStrategyRule

def test_no_cache_strategy_returns_warning():
    result = NoCacheStrategyRule().check(_FakePipeline())
    assert result.severity == Severity.WARNING

def test_empty_string_cache_strategy_returns_warning():
    result = NoCacheStrategyRule().check(_FakePipeline(cache_strategy="  "))
    assert result.severity == Severity.WARNING

def test_cache_strategy_present_passes_no_cache_rule():
    result = NoCacheStrategyRule().check(_FakePipeline(cache_strategy="redis"))
    assert result.severity == Severity.OK


# InvalidCacheStrategyRule

def test_valid_cache_strategies_pass():
    for strategy in ("memory", "disk", "redis", "s3", "none"):
        result = InvalidCacheStrategyRule().check(_FakePipeline(cache_strategy=strategy))
        assert result.severity == Severity.OK, f"Expected OK for '{strategy}'"

def test_invalid_cache_strategy_returns_error():
    result = InvalidCacheStrategyRule().check(_FakePipeline(cache_strategy="memcached"))
    assert result.severity == Severity.ERROR

def test_no_cache_strategy_passes_invalid_rule():
    result = InvalidCacheStrategyRule().check(_FakePipeline())
    assert result.severity == Severity.OK

def test_cache_strategy_case_insensitive():
    result = InvalidCacheStrategyRule().check(_FakePipeline(cache_strategy="Redis"))
    assert result.severity == Severity.OK


# CacheTTLTooLongRule

def test_no_ttl_passes_too_long_rule():
    result = CacheTTLTooLongRule().check(_FakePipeline())
    assert result.severity == Severity.OK

def test_ttl_within_limit_passes():
    result = CacheTTLTooLongRule().check(_FakePipeline(cache_ttl_hours=24))
    assert result.severity == Severity.OK

def test_ttl_too_long_returns_warning():
    result = CacheTTLTooLongRule().check(_FakePipeline(cache_ttl_hours=200))
    assert result.severity == Severity.WARNING

def test_ttl_invalid_type_returns_error():
    result = CacheTTLTooLongRule().check(_FakePipeline(cache_ttl_hours="forever"))
    assert result.severity == Severity.ERROR


# ZeroCacheTTLRule

def test_no_ttl_passes_zero_rule():
    result = ZeroCacheTTLRule().check(_FakePipeline())
    assert result.severity == Severity.OK

def test_zero_ttl_returns_warning():
    result = ZeroCacheTTLRule().check(_FakePipeline(cache_ttl_hours=0))
    assert result.severity == Severity.WARNING

def test_positive_ttl_passes_zero_rule():
    result = ZeroCacheTTLRule().check(_FakePipeline(cache_ttl_hours=1))
    assert result.severity == Severity.OK
