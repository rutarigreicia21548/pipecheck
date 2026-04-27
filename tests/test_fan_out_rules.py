import pytest
from dataclasses import dataclass, field
from typing import Any, Optional

from pipecheck.rules.fan_out_rules import (
    FanInTooHighRule,
    FanOutTooHighRule,
    InvalidFanOutStrategyRule,
    NoFanOutConfigRule,
)


@dataclass
class _FakePipeline:
    fan_out: Optional[Any] = None


# ---------------------------------------------------------------------------
# NoFanOutConfigRule
# ---------------------------------------------------------------------------

def test_no_fan_out_returns_warning():
    result = NoFanOutConfigRule().check(_FakePipeline())
    assert not result.passed
    assert result.severity.name == "WARNING"


def test_empty_dict_fan_out_returns_warning():
    result = NoFanOutConfigRule().check(_FakePipeline(fan_out={}))
    assert not result.passed


def test_fan_out_present_passes_no_fan_out_rule():
    result = NoFanOutConfigRule().check(_FakePipeline(fan_out={"degree": 3}))
    assert result.passed


def test_fan_out_string_passes_no_fan_out_rule():
    result = NoFanOutConfigRule().check(_FakePipeline(fan_out="scatter"))
    assert result.passed


# ---------------------------------------------------------------------------
# FanOutTooHighRule
# ---------------------------------------------------------------------------

def test_no_fan_out_passes_too_high_rule():
    result = FanOutTooHighRule().check(_FakePipeline())
    assert result.passed


def test_fan_out_within_limit_passes():
    result = FanOutTooHighRule().check(_FakePipeline(fan_out={"degree": 5}))
    assert result.passed


def test_fan_out_at_limit_passes():
    result = FanOutTooHighRule().check(_FakePipeline(fan_out={"degree": 10}))
    assert result.passed


def test_fan_out_too_high_returns_error():
    result = FanOutTooHighRule().check(_FakePipeline(fan_out={"degree": 11}))
    assert not result.passed
    assert result.severity.name == "ERROR"
    assert "11" in result.message


def test_fan_out_string_passes_too_high_rule():
    result = FanOutTooHighRule().check(_FakePipeline(fan_out="scatter"))
    assert result.passed


# ---------------------------------------------------------------------------
# FanInTooHighRule
# ---------------------------------------------------------------------------

def test_no_fan_out_passes_fan_in_rule():
    result = FanInTooHighRule().check(_FakePipeline())
    assert result.passed


def test_fan_in_within_limit_passes():
    result = FanInTooHighRule().check(_FakePipeline(fan_out={"degree": 3, "fan_in": 4}))
    assert result.passed


def test_fan_in_too_high_returns_error():
    result = FanInTooHighRule().check(_FakePipeline(fan_out={"degree": 3, "fan_in": 15}))
    assert not result.passed
    assert "15" in result.message


# ---------------------------------------------------------------------------
# InvalidFanOutStrategyRule
# ---------------------------------------------------------------------------

def test_no_fan_out_passes_strategy_rule():
    result = InvalidFanOutStrategyRule().check(_FakePipeline())
    assert result.passed


def test_valid_strategies_pass():
    for strategy in ("scatter", "broadcast", "partition"):
        result = InvalidFanOutStrategyRule().check(
            _FakePipeline(fan_out={"strategy": strategy})
        )
        assert result.passed, f"{strategy} should be valid"


def test_invalid_strategy_returns_error():
    result = InvalidFanOutStrategyRule().check(
        _FakePipeline(fan_out={"strategy": "random"})
    )
    assert not result.passed
    assert "random" in result.message


def test_no_strategy_key_passes_strategy_rule():
    result = InvalidFanOutStrategyRule().check(_FakePipeline(fan_out={"degree": 2}))
    assert result.passed
