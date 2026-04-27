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
class _FakePipeline:
    profiling: Any = None


# --- NoProfilingConfigRule ---

def test_no_profiling_returns_warning():
    result = NoProfilingConfigRule().check(_FakePipeline())
    assert result.severity == Severity.WARNING


def test_empty_dict_profiling_returns_warning():
    result = NoProfilingConfigRule().check(_FakePipeline(profiling={}))
    assert result.severity == Severity.WARNING


def test_profiling_present_passes_no_profiling_rule():
    result = NoProfilingConfigRule().check(_FakePipeline(profiling={"backend": "datadog"}))
    assert result.severity == Severity.OK


def test_profiling_string_passes_no_profiling_rule():
    result = NoProfilingConfigRule().check(_FakePipeline(profiling="datadog"))
    assert result.severity == Severity.OK


# --- InvalidProfilingBackendRule ---

def test_no_profiling_passes_invalid_backend_rule():
    result = InvalidProfilingBackendRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_valid_backends_pass():
    for backend in ("datadog", "opentelemetry", "prometheus", "custom", "none"):
        result = InvalidProfilingBackendRule().check(
            _FakePipeline(profiling={"backend": backend})
        )
        assert result.severity == Severity.OK, f"Expected OK for backend '{backend}'"


def test_invalid_backend_returns_error():
    result = InvalidProfilingBackendRule().check(
        _FakePipeline(profiling={"backend": "splunk"})
    )
    assert result.severity == Severity.ERROR
    assert "splunk" in result.message


def test_missing_backend_key_passes():
    result = InvalidProfilingBackendRule().check(_FakePipeline(profiling={"retention_days": 30}))
    assert result.severity == Severity.OK


# --- SampleRateTooHighRule ---

def test_no_profiling_passes_sample_rate_rule():
    result = SampleRateTooHighRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_sample_rate_within_limit_passes():
    result = SampleRateTooHighRule().check(_FakePipeline(profiling={"sample_rate": 50}))
    assert result.severity == Severity.OK


def test_sample_rate_at_limit_passes():
    result = SampleRateTooHighRule().check(_FakePipeline(profiling={"sample_rate": 100}))
    assert result.severity == Severity.OK


def test_sample_rate_too_high_returns_error():
    result = SampleRateTooHighRule().check(_FakePipeline(profiling={"sample_rate": 150}))
    assert result.severity == Severity.ERROR
    assert "150" in result.message


# --- ProfilingRetentionTooLongRule ---

def test_no_profiling_passes_retention_rule():
    result = ProfilingRetentionTooLongRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_retention_within_limit_passes():
    result = ProfilingRetentionTooLongRule().check(
        _FakePipeline(profiling={"retention_days": 90})
    )
    assert result.severity == Severity.OK


def test_retention_too_long_returns_warning():
    result = ProfilingRetentionTooLongRule().check(
        _FakePipeline(profiling={"retention_days": 400})
    )
    assert result.severity == Severity.WARNING
    assert "400" in result.message
