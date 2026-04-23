import pytest
from dataclasses import dataclass, field
from typing import Any

from pipecheck.rules.rollback_rules import (
    NoRollbackConfigRule,
    InvalidRollbackStrategyRule,
    RollbackWindowTooLargeRule,
)


@dataclass
class _FakePipeline:
    rollback: Any = None


# --- NoRollbackConfigRule ---

def test_no_rollback_returns_warning():
    result = NoRollbackConfigRule().check(_FakePipeline(rollback=None))
    assert not result.passed


def test_empty_dict_rollback_returns_warning():
    result = NoRollbackConfigRule().check(_FakePipeline(rollback={}))
    assert not result.passed


def test_rollback_present_passes_no_rollback_rule():
    result = NoRollbackConfigRule().check(
        _FakePipeline(rollback={"strategy": "full"})
    )
    assert result.passed


def test_rollback_string_passes_no_rollback_rule():
    result = NoRollbackConfigRule().check(_FakePipeline(rollback="full"))
    assert result.passed


# --- InvalidRollbackStrategyRule ---

def test_no_rollback_passes_invalid_strategy_rule():
    result = InvalidRollbackStrategyRule().check(_FakePipeline(rollback=None))
    assert result.passed


def test_rollback_string_passes_invalid_strategy_rule():
    # non-dict rollback skipped
    result = InvalidRollbackStrategyRule().check(_FakePipeline(rollback="full"))
    assert result.passed


def test_valid_strategies_pass():
    for strategy in ("full", "partial", "checkpoint", "none"):
        result = InvalidRollbackStrategyRule().check(
            _FakePipeline(rollback={"strategy": strategy})
        )
        assert result.passed, f"Expected {strategy!r} to pass"


def test_invalid_strategy_returns_error():
    result = InvalidRollbackStrategyRule().check(
        _FakePipeline(rollback={"strategy": "magic"})
    )
    assert not result.passed
    assert "magic" in result.message


def test_missing_strategy_key_passes_invalid_rule():
    result = InvalidRollbackStrategyRule().check(
        _FakePipeline(rollback={"window_days": 7})
    )
    assert result.passed


# --- RollbackWindowTooLargeRule ---

def test_no_rollback_passes_window_rule():
    result = RollbackWindowTooLargeRule().check(_FakePipeline(rollback=None))
    assert result.passed


def test_rollback_without_window_passes_window_rule():
    result = RollbackWindowTooLargeRule().check(
        _FakePipeline(rollback={"strategy": "full"})
    )
    assert result.passed


def test_window_within_limit_passes():
    result = RollbackWindowTooLargeRule().check(
        _FakePipeline(rollback={"strategy": "partial", "window_days": 7})
    )
    assert result.passed


def test_window_at_limit_passes():
    result = RollbackWindowTooLargeRule().check(
        _FakePipeline(rollback={"window_days": 30})
    )
    assert result.passed


def test_window_too_large_returns_warning():
    result = RollbackWindowTooLargeRule().check(
        _FakePipeline(rollback={"window_days": 31})
    )
    assert not result.passed
    assert "31" in result.message
