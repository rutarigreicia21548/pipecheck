from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pipecheck.rules.base import Severity
from pipecheck.rules.freshness_rules import (
    FreshnessTooLenientRule,
    InvalidFreshnessUnitRule,
    NoFreshnessConfigRule,
)

_FRESHNESS_RULES = [
    NoFreshnessConfigRule(),
    InvalidFreshnessUnitRule(),
    FreshnessTooLenientRule(),
]


@dataclass
class _FullPipeline:
    pipeline_id: str = "my_pipeline"
    freshness: Any = None


def _run(pipeline: _FullPipeline):
    return [rule.check(pipeline) for rule in _FRESHNESS_RULES]


def test_valid_freshness_all_pass():
    pipeline = _FullPipeline(freshness={"value": 12, "unit": "hours"})
    results = _run(pipeline)
    assert all(r.severity == Severity.OK for r in results), [
        str(r) for r in results if r.severity != Severity.OK
    ]


def test_missing_freshness_produces_warning():
    pipeline = _FullPipeline(freshness=None)
    results = _run(pipeline)
    warnings = [r for r in results if r.severity == Severity.WARNING]
    assert len(warnings) >= 1
    assert any("freshness" in r.message.lower() for r in warnings)


def test_invalid_unit_produces_error():
    pipeline = _FullPipeline(freshness={"value": 6, "unit": "weeks"})
    results = _run(pipeline)
    errors = [r for r in results if r.severity == Severity.ERROR]
    assert len(errors) == 1
    assert "weeks" in errors[0].message


def test_excessive_freshness_threshold_produces_warning():
    pipeline = _FullPipeline(freshness={"value": 30, "unit": "days"})
    results = _run(pipeline)
    warnings = [r for r in results if r.severity == Severity.WARNING]
    assert any("freshness" in r.message.lower() or "threshold" in r.message.lower() for r in warnings)
