from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from pipecheck.rules.pipeline_health_rules import (
    InvalidHealthStatusRule,
    NoPipelineHealthRule,
    TerminalHealthWithoutDeprecationRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FullPipeline:
    pipeline_id: str = "my_pipeline"
    health: Optional[str] = "active"
    deprecation_policy: Optional[Any] = None


def _health_rules():
    return [
        NoPipelineHealthRule(),
        InvalidHealthStatusRule(),
        TerminalHealthWithoutDeprecationRule(),
    ]


def _check_all(pipeline):
    return [rule.check(pipeline) for rule in _health_rules()]


def test_valid_health_all_pass():
    pipeline = _FullPipeline(health="healthy")
    results = _check_all(pipeline)
    assert all(r.passed for r in results), [r.message for r in results if not r.passed]


def test_missing_health_produces_warning():
    pipeline = _FullPipeline(health=None)
    results = _check_all(pipeline)
    failures = [r for r in results if not r.passed]
    assert len(failures) == 1
    assert failures[0].rule.severity == Severity.WARNING


def test_invalid_health_status_produces_error():
    pipeline = _FullPipeline(health="zombie")
    results = _check_all(pipeline)
    failures = [r for r in results if not r.passed]
    assert any(r.rule.severity == Severity.ERROR for r in failures)


def test_terminal_health_without_deprecation_produces_warning():
    pipeline = _FullPipeline(health="archived", deprecation_policy=None)
    results = _check_all(pipeline)
    failures = [r for r in results if not r.passed]
    assert any("deprecation_policy" in r.message for r in failures)


def test_terminal_health_with_deprecation_passes_terminal_rule():
    pipeline = _FullPipeline(health="archived", deprecation_policy={"date": "2025-06-01"})
    results = _check_all(pipeline)
    terminal_results = [
        r for r in results
        if r.rule.name == "terminal-health-without-deprecation"
    ]
    assert all(r.passed for r in terminal_results)
