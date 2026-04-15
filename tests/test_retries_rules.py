import pytest
from dataclasses import dataclass, field
from typing import Optional, List
from pipecheck.rules.retries_rules import NoRetriesRule, TooManyRetriesRule, NoRetryDelayRule
from pipecheck.rules.base import Severity


@dataclass
class _FakePipeline:
    id: Optional[str] = None
    name: Optional[str] = None
    retries: Optional[int] = None
    retry_delay: Optional[int] = None

    def __post_init__(self):
        if self.id is None and self.name is None:
            self.name = "fake_pipeline"


# --- NoRetriesRule ---

def test_no_retries_returns_warning():
    pipeline = _FakePipeline(id="my_dag")
    result = NoRetriesRule().check(pipeline)
    assert not result.passed
    assert result.severity == Severity.WARNING
    assert "my_dag" in result.message


def test_retries_present_passes_no_retries_rule():
    pipeline = _FakePipeline(id="my_dag", retries=3)
    result = NoRetriesRule().check(pipeline)
    assert result.passed


def test_retries_zero_passes_no_retries_rule():
    """Explicit zero is still a defined value."""
    pipeline = _FakePipeline(id="my_dag", retries=0)
    result = NoRetriesRule().check(pipeline)
    assert result.passed


# --- TooManyRetriesRule ---

def test_retries_within_limit_passes():
    pipeline = _FakePipeline(id="my_dag", retries=3)
    result = TooManyRetriesRule().check(pipeline)
    assert result.passed


def test_retries_at_limit_passes():
    pipeline = _FakePipeline(id="my_dag", retries=5)
    result = TooManyRetriesRule().check(pipeline)
    assert result.passed


def test_retries_exceeds_limit_returns_warning():
    pipeline = _FakePipeline(id="my_dag", retries=10)
    result = TooManyRetriesRule().check(pipeline)
    assert not result.passed
    assert result.severity == Severity.WARNING
    assert "10" in result.message


def test_too_many_retries_custom_limit():
    pipeline = _FakePipeline(id="my_dag", retries=4)
    result = TooManyRetriesRule(max_retries=3).check(pipeline)
    assert not result.passed


def test_no_retries_skips_too_many_check():
    pipeline = _FakePipeline(id="my_dag", retries=None)
    result = TooManyRetriesRule().check(pipeline)
    assert result.passed


# --- NoRetryDelayRule ---

def test_retries_with_delay_passes():
    pipeline = _FakePipeline(id="my_dag", retries=3, retry_delay=300)
    result = NoRetryDelayRule().check(pipeline)
    assert result.passed


def test_retries_without_delay_returns_info():
    pipeline = _FakePipeline(id="my_dag", retries=3)
    result = NoRetryDelayRule().check(pipeline)
    assert not result.passed
    assert result.severity == Severity.INFO
    assert "retry_delay" in result.message


def test_no_retries_no_delay_passes_delay_rule():
    pipeline = _FakePipeline(id="my_dag", retries=None)
    result = NoRetryDelayRule().check(pipeline)
    assert result.passed


def test_zero_retries_no_delay_passes_delay_rule():
    pipeline = _FakePipeline(id="my_dag", retries=0)
    result = NoRetryDelayRule().check(pipeline)
    assert result.passed
