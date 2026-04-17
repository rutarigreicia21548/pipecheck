import pytest
from dataclasses import dataclass, field
from typing import Optional
from pipecheck.rules.base import Severity
from pipecheck.rules.checkpoint_rules import (
    NoCheckpointRule,
    InvalidCheckpointIntervalRule,
    CheckpointIntervalTooLargeRule,
)


@dataclass
class _FakePipeline:
    checkpoint: Optional[str] = None
    checkpoint_interval: Optional[int] = None


# NoCheckpointRule

def test_no_checkpoint_returns_warning():
    p = _FakePipeline()
    result = NoCheckpointRule().check(p)
    assert result.severity == Severity.WARNING


def test_checkpoint_present_passes_no_checkpoint_rule():
    p = _FakePipeline(checkpoint="enabled")
    result = NoCheckpointRule().check(p)
    assert result.severity == Severity.OK


def test_empty_string_checkpoint_returns_warning():
    p = _FakePipeline(checkpoint="")
    result = NoCheckpointRule().check(p)
    assert result.severity == Severity.WARNING


# InvalidCheckpointIntervalRule

def test_no_interval_passes_invalid_interval_rule():
    p = _FakePipeline()
    result = InvalidCheckpointIntervalRule().check(p)
    assert result.severity == Severity.OK


def test_positive_interval_passes():
    p = _FakePipeline(checkpoint_interval=300)
    result = InvalidCheckpointIntervalRule().check(p)
    assert result.severity == Severity.OK


def test_zero_interval_returns_error():
    p = _FakePipeline(checkpoint_interval=0)
    result = InvalidCheckpointIntervalRule().check(p)
    assert result.severity == Severity.ERROR


def test_negative_interval_returns_error():
    p = _FakePipeline(checkpoint_interval=-60)
    result = InvalidCheckpointIntervalRule().check(p)
    assert result.severity == Severity.ERROR


def test_string_interval_returns_error():
    p = _FakePipeline(checkpoint_interval="fast")  # type: ignore
    result = InvalidCheckpointIntervalRule().check(p)
    assert result.severity == Severity.ERROR


# CheckpointIntervalTooLargeRule

def test_no_interval_passes_too_large_rule():
    p = _FakePipeline()
    result = CheckpointIntervalTooLargeRule().check(p)
    assert result.severity == Severity.OK


def test_interval_within_limit_passes():
    p = _FakePipeline(checkpoint_interval=600)
    result = CheckpointIntervalTooLargeRule().check(p)
    assert result.severity == Severity.OK


def test_interval_at_limit_passes():
    p = _FakePipeline(checkpoint_interval=3600)
    result = CheckpointIntervalTooLargeRule().check(p)
    assert result.severity == Severity.OK


def test_interval_exceeds_limit_returns_warning():
    p = _FakePipeline(checkpoint_interval=7200)
    result = CheckpointIntervalTooLargeRule().check(p)
    assert result.severity == Severity.WARNING
    assert "7200" in result.message
