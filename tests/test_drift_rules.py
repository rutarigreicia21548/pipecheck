import pytest

from pipecheck.rules.base import Severity
from pipecheck.rules.drift_rules import (
    DriftThresholdTooHighRule,
    InvalidDriftStrategyRule,
    NoDriftConfigRule,
)


class _FakePipeline:
    def __init__(self, drift=None):
        self.drift = drift


# --- NoDriftConfigRule ---

def test_no_drift_returns_warning():
    result = NoDriftConfigRule().check(_FakePipeline())
    assert not result.passed
    assert result.severity == Severity.WARNING


def test_empty_dict_drift_returns_warning():
    result = NoDriftConfigRule().check(_FakePipeline(drift={}))
    assert not result.passed


def test_drift_dict_present_passes_no_drift_rule():
    result = NoDriftConfigRule().check(_FakePipeline(drift={"strategy": "alert"}))
    assert result.passed


def test_drift_string_passes_no_drift_rule():
    result = NoDriftConfigRule().check(_FakePipeline(drift="alert"))
    assert result.passed


# --- InvalidDriftStrategyRule ---

@pytest.mark.parametrize("strategy", ["alert", "auto-correct", "ignore", "fail"])
def test_valid_drift_strategies_pass(strategy):
    pipeline = _FakePipeline(drift={"strategy": strategy})
    result = InvalidDriftStrategyRule().check(pipeline)
    assert result.passed


def test_invalid_drift_strategy_returns_error():
    pipeline = _FakePipeline(drift={"strategy": "magic"})
    result = InvalidDriftStrategyRule().check(pipeline)
    assert not result.passed
    assert result.severity == Severity.ERROR
    assert "magic" in result.message


def test_no_strategy_key_passes_invalid_strategy_rule():
    pipeline = _FakePipeline(drift={"threshold": 10})
    result = InvalidDriftStrategyRule().check(pipeline)
    assert result.passed


def test_non_dict_drift_passes_invalid_strategy_rule():
    result = InvalidDriftStrategyRule().check(_FakePipeline(drift="alert"))
    assert result.passed


def test_no_drift_passes_invalid_strategy_rule():
    result = InvalidDriftStrategyRule().check(_FakePipeline())
    assert result.passed


# --- DriftThresholdTooHighRule ---

def test_threshold_within_limit_passes():
    pipeline = _FakePipeline(drift={"threshold": 50})
    result = DriftThresholdTooHighRule().check(pipeline)
    assert result.passed


def test_threshold_at_limit_passes():
    pipeline = _FakePipeline(drift={"threshold": 100})
    result = DriftThresholdTooHighRule().check(pipeline)
    assert result.passed


def test_threshold_too_high_returns_warning():
    pipeline = _FakePipeline(drift={"threshold": 150})
    result = DriftThresholdTooHighRule().check(pipeline)
    assert not result.passed
    assert result.severity == Severity.WARNING
    assert "150" in result.message


def test_no_threshold_key_passes_too_high_rule():
    pipeline = _FakePipeline(drift={"strategy": "alert"})
    result = DriftThresholdTooHighRule().check(pipeline)
    assert result.passed


def test_no_drift_passes_threshold_rule():
    result = DriftThresholdTooHighRule().check(_FakePipeline())
    assert result.passed


def test_non_dict_drift_passes_threshold_rule():
    result = DriftThresholdTooHighRule().check(_FakePipeline(drift="alert"))
    assert result.passed
