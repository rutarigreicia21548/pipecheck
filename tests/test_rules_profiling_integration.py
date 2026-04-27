import pytest
from dataclasses import dataclass, field
from typing import Any
from pipecheck.rules.profiling_rules import (
    NoProfilingConfigRule,
    InvalidProfilingBackendRule,
    SampleRateTooHighRule,
    ProfilingRetentionTooLongRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FullPipeline:
    pipeline_id: str = "my_pipeline"
    profiling: Any = None


def _profiling_rules():
    return [
        NoProfilingConfigRule(),
        InvalidProfilingBackendRule(),
        SampleRateTooHighRule(),
        ProfilingRetentionTooLongRule(),
    ]


def _run(pipeline):
    return [rule.check(pipeline) for rule in _profiling_rules()]


def test_valid_profiling_all_pass():
    pipeline = _FullPipeline(
        profiling={
            "backend": "prometheus",
            "sample_rate": 10,
            "retention_days": 60,
        }
    )
    results = _run(pipeline)
    assert all(r.severity == Severity.OK for r in results), [
        r for r in results if r.severity != Severity.OK
    ]


def test_missing_profiling_produces_warning():
    pipeline = _FullPipeline(profiling=None)
    results = _run(pipeline)
    warnings = [r for r in results if r.severity == Severity.WARNING]
    assert any("profiling" in r.message.lower() for r in warnings)


def test_invalid_backend_produces_error():
    pipeline = _FullPipeline(profiling={"backend": "unknown_tool", "sample_rate": 5})
    results = _run(pipeline)
    errors = [r for r in results if r.severity == Severity.ERROR]
    assert len(errors) >= 1
    assert any("unknown_tool" in r.message for r in errors)


def test_excessive_sample_rate_and_retention_produce_failures():
    pipeline = _FullPipeline(
        profiling={
            "backend": "datadog",
            "sample_rate": 200,
            "retention_days": 500,
        }
    )
    results = _run(pipeline)
    non_ok = [r for r in results if r.severity != Severity.OK]
    assert len(non_ok) >= 2
