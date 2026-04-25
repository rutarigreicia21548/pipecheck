import pytest
from dataclasses import dataclass, field
from typing import Any, Optional

from pipecheck.rules.windowing_rules import (
    NoWindowingConfigRule,
    InvalidWindowTypeRule,
    WindowSizeTooLargeRule,
    InvalidWindowUnitRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FakePipeline:
    windowing: Any = None


# --- NoWindowingConfigRule ---

def test_no_windowing_returns_warning():
    result = NoWindowingConfigRule().check(_FakePipeline())
    assert not result.passed
    assert result.severity == Severity.WARNING


def test_empty_dict_windowing_returns_warning():
    result = NoWindowingConfigRule().check(_FakePipeline(windowing={}))
    assert not result.passed
    assert result.severity == Severity.WARNING


def test_windowing_present_passes_no_windowing_rule():
    result = NoWindowingConfigRule().check(_FakePipeline(windowing={"type": "tumbling"}))
    assert result.passed


def test_windowing_string_passes_no_windowing_rule():
    result = NoWindowingConfigRule().check(_FakePipeline(windowing="tumbling"))
    assert result.passed


# --- InvalidWindowTypeRule ---

def test_no_windowing_passes_invalid_type_rule():
    result = InvalidWindowTypeRule().check(_FakePipeline())
    assert result.passed


def test_valid_window_types_pass():
    for wtype in ("tumbling", "sliding", "session", "global"):
        result = InvalidWindowTypeRule().check(_FakePipeline(windowing={"type": wtype}))
        assert result.passed, f"Expected {wtype} to pass"


def test_invalid_window_type_returns_error():
    result = InvalidWindowTypeRule().check(_FakePipeline(windowing={"type": "rolling"}))
    assert not result.passed
    assert result.severity == Severity.ERROR
    assert "rolling" in result.message


# --- WindowSizeTooLargeRule ---

def test_no_windowing_passes_size_rule():
    result = WindowSizeTooLargeRule().check(_FakePipeline())
    assert result.passed


def test_window_size_within_limit_passes():
    result = WindowSizeTooLargeRule().check(_FakePipeline(windowing={"size": 1, "unit": "hours"}))
    assert result.passed


def test_window_size_exactly_7_days_passes():
    result = WindowSizeTooLargeRule().check(_FakePipeline(windowing={"size": 7, "unit": "days"}))
    assert result.passed


def test_window_size_too_large_returns_error():
    result = WindowSizeTooLargeRule().check(_FakePipeline(windowing={"size": 8, "unit": "days"}))
    assert not result.passed
    assert result.severity == Severity.ERROR


def test_window_size_in_seconds_too_large_returns_error():
    result = WindowSizeTooLargeRule().check(_FakePipeline(windowing={"size": 700000, "unit": "seconds"}))
    assert not result.passed


# --- InvalidWindowUnitRule ---

def test_no_windowing_passes_unit_rule():
    result = InvalidWindowUnitRule().check(_FakePipeline())
    assert result.passed


def test_valid_units_pass():
    for unit in ("seconds", "minutes", "hours", "days"):
        result = InvalidWindowUnitRule().check(_FakePipeline(windowing={"unit": unit}))
        assert result.passed, f"Expected {unit} to pass"


def test_invalid_unit_returns_error():
    result = InvalidWindowUnitRule().check(_FakePipeline(windowing={"unit": "weeks"}))
    assert not result.passed
    assert result.severity == Severity.ERROR
    assert "weeks" in result.message
