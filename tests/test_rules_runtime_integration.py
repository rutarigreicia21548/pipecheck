import pytest
from dataclasses import dataclass, field
from pipecheck.rules.base import Severity
from pipecheck.rules.runtime_rules import (
    NoRuntimeLimitRule,
    RuntimeTooLongRule,
    RuntimeWarnThresholdRule,
)


@dataclass
class _FullPipeline:
    pipeline_id: str = "my_pipeline"
    tags: list = field(default_factory=lambda: ["team:data"])
    schedule: str = "@daily"
    max_runtime: object = None


def _runtime_rules():
    return [NoRuntimeLimitRule(), RuntimeTooLongRule(), RuntimeWarnThresholdRule()]


def test_valid_runtime_all_pass():
    pipeline = _FullPipeline(max_runtime=4)
    results = [r.check(pipeline) for r in _runtime_rules()]
    severities = [r.severity for r in results]
    assert all(s == Severity.OK for s in severities)


def test_missing_runtime_produces_warning():
    pipeline = _FullPipeline(max_runtime=None)
    results = [r.check(pipeline) for r in _runtime_rules()]
    warnings = [r for r in results if r.severity == Severity.WARNING]
    assert len(warnings) >= 1
    assert any("max_runtime" in w.message for w in warnings)


def test_excessive_runtime_produces_error():
    pipeline = _FullPipeline(max_runtime=30)
    results = [r.check(pipeline) for r in _runtime_rules()]
    errors = [r for r in results if r.severity == Severity.ERROR]
    assert len(errors) >= 1


def test_long_but_valid_runtime_produces_warning_not_error():
    pipeline = _FullPipeline(max_runtime=12)
    results = [r.check(pipeline) for r in _runtime_rules()]
    assert not any(r.severity == Severity.ERROR for r in results)
    assert any(r.severity == Severity.WARNING for r in results)
