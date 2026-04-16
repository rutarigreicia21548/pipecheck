import pytest
from dataclasses import dataclass
from typing import Optional
from pipecheck.rules.sla_rules import NoSLARule, SLATooLongRule, ZeroSLARule
from pipecheck.rules.base import Severity


@dataclass
class _FakePipeline:
    id: Optional[str] = "my_pipeline"
    sla: Optional[int] = None

    def __post_init__(self):
        pass


def test_no_sla_returns_warning():
    p = _FakePipeline(sla=None)
    result = NoSLARule().check(p)
    assert not result.passed
    assert result.severity == Severity.WARNING


def test_sla_present_passes_no_sla_rule():
    p = _FakePipeline(sla=3600)
    result = NoSLARule().check(p)
    assert result.passed


def test_sla_within_limit_passes_sla_too_long_rule():
    p = _FakePipeline(sla=3600)
    result = SLATooLongRule().check(p)
    assert result.passed


def test_sla_at_limit_passes():
    p = _FakePipeline(sla=86400)
    result = SLATooLongRule().check(p)
    assert result.passed


def test_sla_exceeds_limit_returns_warning():
    p = _FakePipeline(sla=90000)
    result = SLATooLongRule().check(p)
    assert not result.passed
    assert result.severity == Severity.WARNING
    assert "90000" in result.message


def test_none_sla_passes_sla_too_long_rule():
    p = _FakePipeline(sla=None)
    result = SLATooLongRule().check(p)
    assert result.passed


def test_positive_sla_passes_zero_sla_rule():
    p = _FakePipeline(sla=1)
    result = ZeroSLARule().check(p)
    assert result.passed


def test_zero_sla_returns_error():
    p = _FakePipeline(sla=0)
    result = ZeroSLARule().check(p)
    assert not result.passed
    assert result.severity == Severity.ERROR


def test_negative_sla_returns_error():
    p = _FakePipeline(sla=-100)
    result = ZeroSLARule().check(p)
    assert not result.passed


def test_none_sla_passes_zero_sla_rule():
    p = _FakePipeline(sla=None)
    result = ZeroSLARule().check(p)
    assert result.passed
