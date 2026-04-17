import pytest
from dataclasses import dataclass, field
from typing import List, Optional
from pipecheck.rules.data_quality_rules import (
    NoDataQualityChecksRule,
    InvalidCheckTypeRule,
    TooManyChecksRule,
    MAX_QUALITY_CHECKS,
)


@dataclass
class _FakePipeline:
    data_quality_checks: Optional[List[str]] = None


def test_no_checks_returns_warning():
    rule = NoDataQualityChecksRule()
    result = rule.check(_FakePipeline(data_quality_checks=None))
    assert not result.passed


def test_empty_checks_returns_warning():
    rule = NoDataQualityChecksRule()
    result = rule.check(_FakePipeline(data_quality_checks=[]))
    assert not result.passed


def test_checks_present_passes_no_checks_rule():
    rule = NoDataQualityChecksRule()
    result = rule.check(_FakePipeline(data_quality_checks=["not_null"]))
    assert result.passed


def test_valid_check_types_pass_invalid_rule():
    rule = InvalidCheckTypeRule()
    result = rule.check(_FakePipeline(data_quality_checks=["not_null", "unique", "range"]))
    assert result.passed


def test_invalid_check_type_returns_error():
    rule = InvalidCheckTypeRule()
    result = rule.check(_FakePipeline(data_quality_checks=["not_null", "bad_check"]))
    assert not result.passed
    assert "bad_check" in result.message


def test_all_invalid_types_returns_error():
    rule = InvalidCheckTypeRule()
    result = rule.check(_FakePipeline(data_quality_checks=["foo", "bar"]))
    assert not result.passed


def test_no_checks_passes_invalid_type_rule():
    rule = InvalidCheckTypeRule()
    result = rule.check(_FakePipeline(data_quality_checks=None))
    assert result.passed


def test_within_limit_passes_too_many_rule():
    rule = TooManyChecksRule()
    checks = ["not_null"] * MAX_QUALITY_CHECKS
    result = rule.check(_FakePipeline(data_quality_checks=checks))
    assert result.passed


def test_exceeding_limit_returns_warning():
    rule = TooManyChecksRule()
    checks = ["not_null"] * (MAX_QUALITY_CHECKS + 1)
    result = rule.check(_FakePipeline(data_quality_checks=checks))
    assert not result.passed
    assert str(MAX_QUALITY_CHECKS + 1) in result.message


def test_no_checks_passes_too_many_rule():
    rule = TooManyChecksRule()
    result = rule.check(_FakePipeline(data_quality_checks=None))
    assert result.passed
