from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pipecheck.rules.base import Severity
from pipecheck.rules.rate_limit_rules import (
    InvalidRateLimitUnitRule,
    NoRateLimitRule,
    RateLimitTooHighRule,
    ZeroRateLimitRule,
)

_RATE_LIMIT_RULES = [
    NoRateLimitRule(),
    InvalidRateLimitUnitRule(),
    RateLimitTooHighRule(),
    ZeroRateLimitRule(),
]


@dataclass
class _FullPipeline:
    pipeline_id: str = "my_pipeline"
    rate_limit: Any = field(default_factory=lambda: {"requests": 300, "unit": "minute"})


def _run(pipeline):
    return [rule.check(pipeline) for rule in _RATE_LIMIT_RULES]


def test_valid_rate_limit_all_pass():
    results = _run(_FullPipeline())
    severities = {r.severity for r in results}
    assert Severity.ERROR not in severities
    assert Severity.WARNING not in severities


def test_missing_rate_limit_produces_warning():
    pipeline = _FullPipeline(rate_limit=None)
    results = _run(pipeline)
    warnings = [r for r in results if r.severity == Severity.WARNING]
    assert len(warnings) >= 1
    assert any("rate limit" in r.message.lower() for r in warnings)


def test_invalid_unit_produces_error():
    pipeline = _FullPipeline(rate_limit={"requests": 100, "unit": "fortnight"})
    results = _run(pipeline)
    errors = [r for r in results if r.severity == Severity.ERROR]
    assert len(errors) >= 1
    assert any("fortnight" in r.message for r in errors)


def test_zero_requests_produces_error():
    pipeline = _FullPipeline(rate_limit={"requests": 0, "unit": "hour"})
    results = _run(pipeline)
    errors = [r for r in results if r.severity == Severity.ERROR]
    assert any("zero" in r.message.lower() or "0" in r.message for r in errors)


def test_excessive_requests_produces_error():
    pipeline = _FullPipeline(rate_limit={"requests": 500_000, "unit": "second"})
    results = _run(pipeline)
    errors = [r for r in results if r.severity == Severity.ERROR]
    assert any("500000" in r.message for r in errors)
