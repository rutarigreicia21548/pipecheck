import pytest
from dataclasses import dataclass, field
from typing import Any
from pipecheck.rules.observability_rules import (
    NoObservabilityConfigRule,
    InvalidTracingBackendRule,
    InvalidMetricsBackendRule,
    TooManyCustomMetricsRule,
    MAX_CUSTOM_METRICS,
)


@dataclass
class _FakePipeline:
    observability: Any = None


# --- NoObservabilityConfigRule ---

def test_no_observability_returns_warning():
    result = NoObservabilityConfigRule().check(_FakePipeline())
    assert not result.passed


def test_empty_dict_observability_returns_warning():
    result = NoObservabilityConfigRule().check(_FakePipeline(observability={}))
    assert not result.passed


def test_observability_present_passes_no_obs_rule():
    result = NoObservabilityConfigRule().check(
        _FakePipeline(observability={"tracing_backend": "datadog"})
    )
    assert result.passed


# --- InvalidTracingBackendRule ---

def test_no_observability_passes_invalid_tracing_rule():
    result = InvalidTracingBackendRule().check(_FakePipeline())
    assert result.passed


def test_valid_tracing_backends_pass():
    for backend in ["opentelemetry", "datadog", "jaeger", "zipkin", "honeycomb"]:
        result = InvalidTracingBackendRule().check(
            _FakePipeline(observability={"tracing_backend": backend})
        )
        assert result.passed, f"{backend} should be valid"


def test_invalid_tracing_backend_returns_error():
    result = InvalidTracingBackendRule().check(
        _FakePipeline(observability={"tracing_backend": "newrelic"})
    )
    assert not result.passed
    assert "newrelic" in result.message


def test_tracing_backend_case_insensitive():
    result = InvalidTracingBackendRule().check(
        _FakePipeline(observability={"tracing_backend": "DataDog"})
    )
    assert result.passed


# --- InvalidMetricsBackendRule ---

def test_no_observability_passes_invalid_metrics_rule():
    result = InvalidMetricsBackendRule().check(_FakePipeline())
    assert result.passed


def test_valid_metrics_backends_pass():
    for backend in ["prometheus", "datadog", "statsd", "cloudwatch", "grafana"]:
        result = InvalidMetricsBackendRule().check(
            _FakePipeline(observability={"metrics_backend": backend})
        )
        assert result.passed, f"{backend} should be valid"


def test_invalid_metrics_backend_returns_error():
    result = InvalidMetricsBackendRule().check(
        _FakePipeline(observability={"metrics_backend": "influxdb"})
    )
    assert not result.passed
    assert "influxdb" in result.message


# --- TooManyCustomMetricsRule ---

def test_no_custom_metrics_passes_too_many_rule():
    result = TooManyCustomMetricsRule().check(
        _FakePipeline(observability={"tracing_backend": "datadog"})
    )
    assert result.passed


def test_metrics_within_limit_passes():
    metrics = [f"metric_{i}" for i in range(MAX_CUSTOM_METRICS)]
    result = TooManyCustomMetricsRule().check(
        _FakePipeline(observability={"custom_metrics": metrics})
    )
    assert result.passed


def test_too_many_custom_metrics_returns_warning():
    metrics = [f"metric_{i}" for i in range(MAX_CUSTOM_METRICS + 1)]
    result = TooManyCustomMetricsRule().check(
        _FakePipeline(observability={"custom_metrics": metrics})
    )
    assert not result.passed
    assert str(MAX_CUSTOM_METRICS + 1) in result.message
