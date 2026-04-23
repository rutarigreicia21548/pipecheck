import pytest
from dataclasses import dataclass, field
from typing import Any
from pipecheck.rules.observability_rules import (
    NoObservabilityConfigRule,
    InvalidTracingBackendRule,
    InvalidMetricsBackendRule,
    TooManyCustomMetricsRule,
)


@dataclass
class _FullPipeline:
    pipeline_id: str = "my_pipeline"
    observability: Any = None


def _obs_rules(pipeline):
    rules = [
        NoObservabilityConfigRule(),
        InvalidTracingBackendRule(),
        InvalidMetricsBackendRule(),
        TooManyCustomMetricsRule(),
    ]
    return [r.check(pipeline) for r in rules]


def test_valid_observability_all_pass():
    pipeline = _FullPipeline(
        observability={
            "tracing_backend": "opentelemetry",
            "metrics_backend": "prometheus",
            "custom_metrics": ["latency_p99", "error_rate"],
        }
    )
    results = _obs_rules(pipeline)
    assert all(r.passed for r in results), [r.message for r in results if not r.passed]


def test_missing_observability_produces_warning():
    pipeline = _FullPipeline(observability=None)
    results = _obs_rules(pipeline)
    failures = [r for r in results if not r.passed]
    assert len(failures) == 1
    assert failures[0].rule == "no_observability_config"


def test_invalid_backends_produce_errors():
    pipeline = _FullPipeline(
        observability={
            "tracing_backend": "bad_tracer",
            "metrics_backend": "bad_metrics",
        }
    )
    results = _obs_rules(pipeline)
    failed_rules = {r.rule for r in results if not r.passed}
    assert "invalid_tracing_backend" in failed_rules
    assert "invalid_metrics_backend" in failed_rules
