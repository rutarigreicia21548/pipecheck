import pytest
from dataclasses import dataclass, field
from pipecheck.rules.cost_rules import (
    NoCostEstimateRule,
    CostEstimateTooHighRule,
    InvalidCostTierRule,
    MAX_COST_LIMIT,
    WARN_COST_LIMIT,
)
from pipecheck.rules.base import Severity


@dataclass
class _FakePipeline:
    cost_estimate: object = None
    cost_tier: object = None


# NoCostEstimateRule

def test_no_cost_returns_warning():
    result = NoCostEstimateRule().check(_FakePipeline())
    assert result.severity == Severity.WARNING


def test_cost_estimate_present_passes_no_cost_rule():
    result = NoCostEstimateRule().check(_FakePipeline(cost_estimate=100.0))
    assert result.severity == Severity.OK


def test_cost_tier_present_passes_no_cost_rule():
    result = NoCostEstimateRule().check(_FakePipeline(cost_tier="low"))
    assert result.severity == Severity.OK


# CostEstimateTooHighRule

def test_no_cost_estimate_passes_too_high_rule():
    result = CostEstimateTooHighRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_cost_within_limit_passes():
    result = CostEstimateTooHighRule().check(_FakePipeline(cost_estimate=100.0))
    assert result.severity == Severity.OK


def test_cost_above_warn_limit_returns_warning():
    result = CostEstimateTooHighRule().check(_FakePipeline(cost_estimate=WARN_COST_LIMIT + 1))
    assert result.severity == Severity.WARNING


def test_cost_above_max_limit_returns_error():
    result = CostEstimateTooHighRule().check(_FakePipeline(cost_estimate=MAX_COST_LIMIT + 1))
    assert result.severity == Severity.ERROR


def test_non_numeric_cost_returns_error():
    result = CostEstimateTooHighRule().check(_FakePipeline(cost_estimate="expensive"))
    assert result.severity == Severity.ERROR


def test_cost_at_exact_max_passes():
    result = CostEstimateTooHighRule().check(_FakePipeline(cost_estimate=MAX_COST_LIMIT))
    assert result.severity == Severity.OK


# InvalidCostTierRule

def test_no_cost_tier_passes_invalid_tier_rule():
    result = InvalidCostTierRule().check(_FakePipeline())
    assert result.severity == Severity.OK


@pytest.mark.parametrize("tier", ["low", "medium", "high", "critical"])
def test_valid_cost_tiers_pass(tier):
    result = InvalidCostTierRule().check(_FakePipeline(cost_tier=tier))
    assert result.severity == Severity.OK


def test_invalid_cost_tier_returns_error():
    result = InvalidCostTierRule().check(_FakePipeline(cost_tier="expensive"))
    assert result.severity == Severity.ERROR
    assert "expensive" in result.message


def test_empty_cost_tier_passes_invalid_tier_rule():
    result = InvalidCostTierRule().check(_FakePipeline(cost_tier=""))
    assert result.severity == Severity.OK
