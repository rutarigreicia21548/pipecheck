from __future__ import annotations

import pytest

from pipecheck.rules.quota_rules import (
    InvalidQuotaUnitRule,
    NoQuotaConfigRule,
    QuotaLimitTooHighRule,
)
from pipecheck.rules.base import Severity


class _FakePipeline:
    def __init__(self, quota=None):
        self.quota = quota


# ---------------------------------------------------------------------------
# NoQuotaConfigRule
# ---------------------------------------------------------------------------

def test_no_quota_returns_warning():
    result = NoQuotaConfigRule().check(_FakePipeline())
    assert not result.passed
    assert result.severity == Severity.WARNING


def test_empty_dict_quota_returns_warning():
    result = NoQuotaConfigRule().check(_FakePipeline(quota={}))
    assert not result.passed


def test_quota_present_passes_no_quota_rule():
    result = NoQuotaConfigRule().check(_FakePipeline(quota={"limit": 500, "unit": "requests/min"}))
    assert result.passed


def test_quota_string_passes_no_quota_rule():
    result = NoQuotaConfigRule().check(_FakePipeline(quota="1000/hour"))
    assert result.passed


# ---------------------------------------------------------------------------
# InvalidQuotaUnitRule
# ---------------------------------------------------------------------------

def test_no_quota_passes_invalid_unit_rule():
    result = InvalidQuotaUnitRule().check(_FakePipeline())
    assert result.passed


def test_valid_quota_units_pass():
    for unit in ("requests/min", "requests/hour", "requests/day", "calls/min", "calls/hour"):
        result = InvalidQuotaUnitRule().check(_FakePipeline(quota={"unit": unit, "limit": 100}))
        assert result.passed, f"Expected {unit!r} to pass"


def test_invalid_quota_unit_returns_error():
    result = InvalidQuotaUnitRule().check(_FakePipeline(quota={"unit": "per_second", "limit": 50}))
    assert not result.passed
    assert result.severity == Severity.ERROR
    assert "per_second" in result.message


def test_missing_unit_key_passes_invalid_unit_rule():
    result = InvalidQuotaUnitRule().check(_FakePipeline(quota={"limit": 200}))
    assert result.passed


# ---------------------------------------------------------------------------
# QuotaLimitTooHighRule
# ---------------------------------------------------------------------------

def test_no_quota_passes_too_high_rule():
    result = QuotaLimitTooHighRule().check(_FakePipeline())
    assert result.passed


def test_quota_limit_within_bounds_passes():
    result = QuotaLimitTooHighRule().check(_FakePipeline(quota={"limit": 1000, "unit": "requests/min"}))
    assert result.passed


def test_quota_limit_at_max_passes():
    result = QuotaLimitTooHighRule().check(_FakePipeline(quota={"limit": 100_000, "unit": "requests/hour"}))
    assert result.passed


def test_quota_limit_too_high_returns_warning():
    result = QuotaLimitTooHighRule().check(_FakePipeline(quota={"limit": 200_000, "unit": "requests/hour"}))
    assert not result.passed
    assert result.severity == Severity.WARNING
    assert "200000" in result.message


def test_missing_limit_key_passes_too_high_rule():
    result = QuotaLimitTooHighRule().check(_FakePipeline(quota={"unit": "requests/min"}))
    assert result.passed
