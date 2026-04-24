from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from pipecheck.rules.base import Severity
from pipecheck.rules.rate_limit_rules import (
    InvalidRateLimitUnitRule,
    NoRateLimitRule,
    RateLimitTooHighRule,
    ZeroRateLimitRule,
)


@dataclass
class _FakePipeline:
    rate_limit: Any = None


# ---------------------------------------------------------------------------
# NoRateLimitRule
# ---------------------------------------------------------------------------

def test_no_rate_limit_returns_warning():
    result = NoRateLimitRule().check(_FakePipeline())
    assert result.severity == Severity.WARNING


def test_empty_dict_rate_limit_returns_warning():
    result = NoRateLimitRule().check(_FakePipeline(rate_limit={}))
    assert result.severity == Severity.WARNING


def test_rate_limit_present_passes_no_rate_limit_rule():
    result = NoRateLimitRule().check(_FakePipeline(rate_limit={"requests": 100, "unit": "minute"}))
    assert result.severity == Severity.OK


def test_rate_limit_string_passes_no_rate_limit_rule():
    result = NoRateLimitRule().check(_FakePipeline(rate_limit="100/minute"))
    assert result.severity == Severity.OK


# ---------------------------------------------------------------------------
# InvalidRateLimitUnitRule
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("unit", ["second", "minute", "hour", "day"])
def test_valid_units_pass_invalid_unit_rule(unit):
    result = InvalidRateLimitUnitRule().check(_FakePipeline(rate_limit={"requests": 10, "unit": unit}))
    assert result.severity == Severity.OK


def test_invalid_unit_returns_error():
    result = InvalidRateLimitUnitRule().check(_FakePipeline(rate_limit={"requests": 10, "unit": "week"}))
    assert result.severity == Severity.ERROR
    assert "week" in result.message


def test_no_unit_key_passes_invalid_unit_rule():
    result = InvalidRateLimitUnitRule().check(_FakePipeline(rate_limit={"requests": 10}))
    assert result.severity == Severity.OK


def test_non_dict_rate_limit_passes_invalid_unit_rule():
    result = InvalidRateLimitUnitRule().check(_FakePipeline(rate_limit="100/minute"))
    assert result.severity == Severity.OK


# ---------------------------------------------------------------------------
# RateLimitTooHighRule
# ---------------------------------------------------------------------------

def test_rate_limit_within_limit_passes():
    result = RateLimitTooHighRule().check(_FakePipeline(rate_limit={"requests": 500, "unit": "minute"}))
    assert result.severity == Severity.OK


def test_rate_limit_too_high_returns_error():
    result = RateLimitTooHighRule().check(_FakePipeline(rate_limit={"requests": 99999, "unit": "minute"}))
    assert result.severity == Severity.ERROR
    assert "99999" in result.message


def test_rate_limit_at_exact_max_passes():
    result = RateLimitTooHighRule().check(_FakePipeline(rate_limit={"requests": 10_000, "unit": "hour"}))
    assert result.severity == Severity.OK


def test_no_requests_key_passes_too_high_rule():
    result = RateLimitTooHighRule().check(_FakePipeline(rate_limit={"unit": "hour"}))
    assert result.severity == Severity.OK


# ---------------------------------------------------------------------------
# ZeroRateLimitRule
# ---------------------------------------------------------------------------

def test_zero_requests_returns_error():
    result = ZeroRateLimitRule().check(_FakePipeline(rate_limit={"requests": 0, "unit": "minute"}))
    assert result.severity == Severity.ERROR
    assert "0" in result.message


def test_nonzero_requests_passes_zero_rule():
    result = ZeroRateLimitRule().check(_FakePipeline(rate_limit={"requests": 1, "unit": "minute"}))
    assert result.severity == Severity.OK


def test_no_rate_limit_passes_zero_rule():
    result = ZeroRateLimitRule().check(_FakePipeline())
    assert result.severity == Severity.OK
