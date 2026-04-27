from __future__ import annotations

import pytest

from pipecheck.rules.sampling_rules import (
    HighSamplingRateRule,
    InvalidSamplingStrategyRule,
    NoSamplingConfigRule,
    SamplingRateOutOfRangeRule,
)


class _FakePipeline:
    def __init__(self, sampling=None):
        self.sampling = sampling


# ---------------------------------------------------------------------------
# NoSamplingConfigRule
# ---------------------------------------------------------------------------

def test_no_sampling_returns_warning():
    result = NoSamplingConfigRule().check(_FakePipeline(sampling=None))
    assert not result.passed
    assert result.severity.name == "WARNING"


def test_empty_dict_sampling_returns_warning():
    result = NoSamplingConfigRule().check(_FakePipeline(sampling={}))
    assert not result.passed


def test_sampling_present_passes_no_sampling_rule():
    result = NoSamplingConfigRule().check(_FakePipeline(sampling={"strategy": "random"}))
    assert result.passed


def test_sampling_string_passes_no_sampling_rule():
    result = NoSamplingConfigRule().check(_FakePipeline(sampling="random"))
    assert result.passed


# ---------------------------------------------------------------------------
# InvalidSamplingStrategyRule
# ---------------------------------------------------------------------------

def test_no_sampling_passes_invalid_strategy_rule():
    result = InvalidSamplingStrategyRule().check(_FakePipeline(sampling=None))
    assert result.passed


def test_non_dict_sampling_passes_invalid_strategy_rule():
    result = InvalidSamplingStrategyRule().check(_FakePipeline(sampling="random"))
    assert result.passed


@pytest.mark.parametrize("strategy", ["random", "systematic", "stratified", "reservoir", "bernoulli"])
def test_valid_strategies_pass(strategy):
    result = InvalidSamplingStrategyRule().check(_FakePipeline(sampling={"strategy": strategy}))
    assert result.passed


@pytest.mark.parametrize("strategy", ["uniform", "cluster", "quota", ""])
def test_invalid_strategies_fail(strategy):
    result = InvalidSamplingStrategyRule().check(_FakePipeline(sampling={"strategy": strategy}))
    assert not result.passed
    assert result.severity.name == "ERROR"


def test_missing_strategy_key_passes_invalid_rule():
    result = InvalidSamplingStrategyRule().check(_FakePipeline(sampling={"sample_rate": 0.1}))
    assert result.passed


# ---------------------------------------------------------------------------
# SamplingRateOutOfRangeRule
# ---------------------------------------------------------------------------

def test_no_sampling_passes_range_rule():
    result = SamplingRateOutOfRangeRule().check(_FakePipeline(sampling=None))
    assert result.passed


@pytest.mark.parametrize("rate", [0.0, 0.1, 0.5, 1.0])
def test_valid_rates_pass_range_rule(rate):
    result = SamplingRateOutOfRangeRule().check(_FakePipeline(sampling={"sample_rate": rate}))
    assert result.passed


@pytest.mark.parametrize("rate", [-0.1, 1.1, 2.0, -100])
def test_out_of_range_rates_fail(rate):
    result = SamplingRateOutOfRangeRule().check(_FakePipeline(sampling={"sample_rate": rate}))
    assert not result.passed
    assert result.severity.name == "ERROR"


def test_non_numeric_rate_fails_range_rule():
    result = SamplingRateOutOfRangeRule().check(_FakePipeline(sampling={"sample_rate": "high"}))
    assert not result.passed


# ---------------------------------------------------------------------------
# HighSamplingRateRule
# ---------------------------------------------------------------------------

def test_no_sampling_passes_high_rate_rule():
    result = HighSamplingRateRule().check(_FakePipeline(sampling=None))
    assert result.passed


@pytest.mark.parametrize("rate", [0.0, 0.1, 0.5])
def test_low_or_boundary_rates_pass_high_rate_rule(rate):
    result = HighSamplingRateRule().check(_FakePipeline(sampling={"sample_rate": rate}))
    assert result.passed


@pytest.mark.parametrize("rate", [0.51, 0.75, 1.0])
def test_high_rates_trigger_warning(rate):
    result = HighSamplingRateRule().check(_FakePipeline(sampling={"sample_rate": rate}))
    assert not result.passed
    assert result.severity.name == "WARNING"


def test_non_numeric_rate_passes_high_rate_rule_gracefully():
    result = HighSamplingRateRule().check(_FakePipeline(sampling={"sample_rate": "unknown"}))
    assert result.passed
