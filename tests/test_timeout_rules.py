import pytest
from dataclasses import dataclass, field
from typing import Optional, List
from pipecheck.rules.timeout_rules import NoTimeoutRule, TimeoutTooLongRule, ZeroTimeoutRule
from pipecheck.rules.base import Severity


@dataclass
class _FakePipeline:
    id: Optional[str] = "my_pipeline"
    name: Optional[str] = None
    timeout: Optional[int] = None
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.name is None:
            self.name = self.id


# --- NoTimeoutRule ---

def test_no_timeout_returns_warning():
    pipeline = _FakePipeline(timeout=None)
    result = NoTimeoutRule().check(pipeline)
    assert not result.passed
    assert result.severity == Severity.WARNING


def test_timeout_present_passes_no_timeout_rule():
    pipeline = _FakePipeline(timeout=600)
    result = NoTimeoutRule().check(pipeline)
    assert result.passed


# --- TimeoutTooLongRule ---

def test_timeout_within_limit_passes():
    pipeline = _FakePipeline(timeout=1800)
    result = TimeoutTooLongRule(max_seconds=3600).check(pipeline)
    assert result.passed


def test_timeout_exceeds_limit_fails():
    pipeline = _FakePipeline(timeout=7200)
    result = TimeoutTooLongRule(max_seconds=3600).check(pipeline)
    assert not result.passed
    assert result.severity == Severity.WARNING
    assert "7200" in result.message
    assert "3600" in result.message


def test_timeout_exactly_at_limit_passes():
    pipeline = _FakePipeline(timeout=3600)
    result = TimeoutTooLongRule(max_seconds=3600).check(pipeline)
    assert result.passed


def test_no_timeout_passes_too_long_rule():
    pipeline = _FakePipeline(timeout=None)
    result = TimeoutTooLongRule().check(pipeline)
    assert result.passed


def test_custom_max_seconds():
    pipeline = _FakePipeline(timeout=500)
    result = TimeoutTooLongRule(max_seconds=300).check(pipeline)
    assert not result.passed


# --- ZeroTimeoutRule ---

def test_zero_timeout_fails():
    pipeline = _FakePipeline(timeout=0)
    result = ZeroTimeoutRule().check(pipeline)
    assert not result.passed
    assert result.severity == Severity.ERROR


def test_negative_timeout_fails():
    pipeline = _FakePipeline(timeout=-10)
    result = ZeroTimeoutRule().check(pipeline)
    assert not result.passed
    assert "-10" in result.message


def test_positive_timeout_passes_zero_rule():
    pipeline = _FakePipeline(timeout=30)
    result = ZeroTimeoutRule().check(pipeline)
    assert result.passed


def test_none_timeout_passes_zero_rule():
    pipeline = _FakePipeline(timeout=None)
    result = ZeroTimeoutRule().check(pipeline)
    assert result.passed
