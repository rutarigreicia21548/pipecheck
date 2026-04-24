from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from pipecheck.rules.base import Severity
from pipecheck.rules.freshness_rules import (
    FreshnessTooLenientRule,
    InvalidFreshnessUnitRule,
    NoFreshnessConfigRule,
)


@dataclass
class _FakePipeline:
    freshness: Any = None


# --- NoFreshnessConfigRule ---

def test_no_freshness_returns_warning():
    result = NoFreshnessConfigRule().check(_FakePipeline())
    assert result.severity == Severity.WARNING


def test_empty_dict_freshness_returns_warning():
    result = NoFreshnessConfigRule().check(_FakePipeline(freshness={}))
    assert result.severity == Severity.WARNING


def test_freshness_dict_present_passes_no_freshness_rule():
    result = NoFreshnessConfigRule().check(_FakePipeline(freshness={"value": 6, "unit": "hours"}))
    assert result.severity == Severity.OK


def test_freshness_string_passes_no_freshness_rule():
    result = NoFreshnessConfigRule().check(_FakePipeline(freshness="6h"))
    assert result.severity == Severity.OK


# --- InvalidFreshnessUnitRule ---

def test_no_freshness_skips_invalid_unit_rule():
    result = InvalidFreshnessUnitRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_freshness_string_skips_invalid_unit_rule():
    result = InvalidFreshnessUnitRule().check(_FakePipeline(freshness="6h"))
    assert result.severity == Severity.OK


@pytest.mark.parametrize("unit", ["seconds", "minutes", "hours", "days"])
def test_valid_freshness_units_pass(unit):
    result = InvalidFreshnessUnitRule().check(_FakePipeline(freshness={"value": 1, "unit": unit}))
    assert result.severity == Severity.OK


@pytest.mark.parametrize("unit", ["hrs", "ms", "weeks", "", "HOURS"])
def test_invalid_freshness_units_return_error(unit):
    result = InvalidFreshnessUnitRule().check(_FakePipeline(freshness={"value": 1, "unit": unit}))
    assert result.severity == Severity.ERROR
    assert unit in result.message


# --- FreshnessTooLenientRule ---

def test_no_freshness_skips_too_lenient_rule():
    result = FreshnessTooLenientRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_freshness_within_limit_passes():
    result = FreshnessTooLenientRule().check(_FakePipeline(freshness={"value": 24, "unit": "hours"}))
    assert result.severity == Severity.OK


def test_freshness_exactly_at_limit_passes():
    result = FreshnessTooLenientRule().check(_FakePipeline(freshness={"value": 168, "unit": "hours"}))
    assert result.severity == Severity.OK


def test_freshness_exceeds_limit_returns_warning():
    result = FreshnessTooLenientRule().check(_FakePipeline(freshness={"value": 8, "unit": "days"}))
    assert result.severity == Severity.WARNING


def test_freshness_in_seconds_within_limit_passes():
    result = FreshnessTooLenientRule().check(_FakePipeline(freshness={"value": 3600, "unit": "seconds"}))
    assert result.severity == Severity.OK


def test_no_value_in_freshness_dict_skips_too_lenient_rule():
    result = FreshnessTooLenientRule().check(_FakePipeline(freshness={"unit": "hours"}))
    assert result.severity == Severity.OK
