import pytest
from dataclasses import dataclass
from typing import Optional
from pipecheck.rules.cache_rules import (
    NoCacheStrategyRule,
    InvalidCacheStrategyRule,
    CacheTTLTooLongRule,
    ZeroCacheTTLRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FullPipeline:
    pipeline_id: str = "my_pipeline"
    cache_strategy: Optional[str] = None
    cache_ttl_hours: Optional[float] = None


def _cache_rules():
    return [
        NoCacheStrategyRule(),
        InvalidCacheStrategyRule(),
        CacheTTLTooLongRule(),
        ZeroCacheTTLRule(),
    ]


def test_valid_cache_config_all_pass():
    pipeline = _FullPipeline(cache_strategy="redis", cache_ttl_hours=12)
    results = [r.check(pipeline) for r in _cache_rules()]
    assert all(r.severity == Severity.OK for r in results)


def test_missing_cache_strategy_produces_warning():
    pipeline = _FullPipeline(cache_ttl_hours=12)
    results = [r.check(pipeline) for r in _cache_rules()]
    severities = {r.rule_id: r.severity for r in results}
    assert severities["NO_CACHE_STRATEGY"] == Severity.WARNING
    assert severities["INVALID_CACHE_STRATEGY"] == Severity.OK


def test_invalid_strategy_and_excessive_ttl_produce_failures():
    pipeline = _FullPipeline(cache_strategy="memcached", cache_ttl_hours=500)
    results = {r.check(pipeline).rule_id: r.check(pipeline) for r in _cache_rules()}
    assert results["INVALID_CACHE_STRATEGY"].severity == Severity.ERROR
    assert results["CACHE_TTL_TOO_LONG"].severity == Severity.WARNING
