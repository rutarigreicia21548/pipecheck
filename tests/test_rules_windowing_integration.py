import pytest
from dataclasses import dataclass, field
from typing import Any, Optional

from pipecheck.rules.windowing_rules import (
    NoWindowingConfigRule,
    InvalidWindowTypeRule,
    WindowSizeTooLargeRule,
    InvalidWindowUnitRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FullPipeline:
    windowing: Any = None


_WINDOWING_RULES = [
    NoWindowingConfigRule(),
    InvalidWindowTypeRule(),
    WindowSizeTooLargeRule(),
    InvalidWindowUnitRule(),
]


def _run(pipeline):
    return [r.check(pipeline) for r in _WINDOWING_RULES]


def test_valid_windowing_all_pass():
    pipeline = _FullPipeline(windowing={"type": "tumbling", "size": 5, "unit": "minutes"})
    results = _run(pipeline)
    assert all(r.passed for r in results), [r.message for r in results if not r.passed]


def test_missing_windowing_produces_warning():
    results = _run(_FullPipeline())
    failures = [r for r in results if not r.passed]
    assert len(failures) == 1
    assert failures[0].severity == Severity.WARNING


def test_invalid_type_produces_error():
    pipeline = _FullPipeline(windowing={"type": "circular", "size": 10, "unit": "minutes"})
    results = _run(pipeline)
    errors = [r for r in results if not r.passed and r.severity == Severity.ERROR]
    assert any("circular" in r.message for r in errors)


def test_oversized_window_produces_error():
    pipeline = _FullPipeline(windowing={"type": "sliding", "size": 30, "unit": "days"})
    results = _run(pipeline)
    errors = [r for r in results if not r.passed and r.severity == Severity.ERROR]
    assert len(errors) >= 1
