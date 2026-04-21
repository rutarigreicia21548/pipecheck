import pytest
from dataclasses import dataclass, field
from pipecheck.rules.base import Severity
from pipecheck.rules.runtime_rules import (
    NoRuntimeLimitRule,
    RuntimeTooLongRule,
    RuntimeWarnThresholdRule,
)


@dataclass
class _FakePipeline:
    max_runtime: object = None


# --- NoRuntimeLimitRule ---

def test_no_runtime_returns_warning():
    result = NoRuntimeLimitRule().check(_FakePipeline())
    assert result.severity == Severity.WARNING


def test_runtime_present_passes_no_runtime_rule():
    result = NoRuntimeLimitRule().check(_FakePipeline(max_runtime=4))
    assert result.severity == Severity.OK


def test_runtime_zero_passes_no_runtime_rule():
    result = NoRuntimeLimitRule().check(_FakePipeline(max_runtime=0))
    assert result.severity == Severity.OK


# --- RuntimeTooLongRule ---

def test_no_runtime_passes_too_long_rule():
    result = RuntimeTooLongRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_runtime_within_limit_passes():
    result = RuntimeTooLongRule().check(_FakePipeline(max_runtime=6))
    assert result.severity == Severity.OK


def test_runtime_at_exact_limit_passes():
    result = RuntimeTooLongRule().check(_FakePipeline(max_runtime=24))
    assert result.severity == Severity.OK


def test_runtime_too_long_returns_error():
    result = RuntimeTooLongRule().check(_FakePipeline(max_runtime=25))
    assert result.severity == Severity.ERROR
    assert "25" in result.message


def test_runtime_non_numeric_returns_error():
    result = RuntimeTooLongRule().check(_FakePipeline(max_runtime="fast"))
    assert result.severity == Severity.ERROR
    assert "fast" in result.message


def test_runtime_float_string_is_valid():
    result = RuntimeTooLongRule().check(_FakePipeline(max_runtime="3.5"))
    assert result.severity == Severity.OK


# --- RuntimeWarnThresholdRule ---

def test_no_runtime_passes_warn_threshold_rule():
    result = RuntimeWarnThresholdRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_runtime_below_warn_threshold_passes():
    result = RuntimeWarnThresholdRule().check(_FakePipeline(max_runtime=4))
    assert result.severity == Severity.OK


def test_runtime_at_warn_threshold_passes():
    result = RuntimeWarnThresholdRule().check(_FakePipeline(max_runtime=8))
    assert result.severity == Severity.OK


def test_runtime_above_warn_threshold_returns_warning():
    result = RuntimeWarnThresholdRule().check(_FakePipeline(max_runtime=10))
    assert result.severity == Severity.WARNING
    assert "10" in result.message


def test_non_numeric_runtime_passes_warn_threshold_rule():
    result = RuntimeWarnThresholdRule().check(_FakePipeline(max_runtime="unknown"))
    assert result.severity == Severity.OK
