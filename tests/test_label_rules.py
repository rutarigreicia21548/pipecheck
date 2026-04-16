import pytest
from dataclasses import dataclass, field
from typing import List, Optional
from pipecheck.rules.label_rules import (
    NoLabelsRule,
    TooManyLabelsRule,
    InvalidLabelFormatRule,
    ReservedLabelRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FakePipeline:
    labels: Optional[List[str]] = None

    def __post_init__(self):
        pass


def test_no_labels_returns_warning():
    p = _FakePipeline(labels=None)
    result = NoLabelsRule().check(p)
    assert result.severity == Severity.WARNING


def test_empty_labels_returns_warning():
    p = _FakePipeline(labels=[])
    result = NoLabelsRule().check(p)
    assert result.severity == Severity.WARNING


def test_labels_present_passes_no_labels_rule():
    p = _FakePipeline(labels=["team-data"])
    result = NoLabelsRule().check(p)
    assert result.severity == Severity.OK


def test_too_many_labels_returns_error():
    p = _FakePipeline(labels=[f"label-{i}" for i in range(11)])
    result = TooManyLabelsRule().check(p)
    assert result.severity == Severity.ERROR


def test_labels_within_limit_passes():
    p = _FakePipeline(labels=["a", "b", "c"])
    result = TooManyLabelsRule().check(p)
    assert result.severity == Severity.OK


def test_none_labels_passes_too_many_rule():
    p = _FakePipeline(labels=None)
    result = TooManyLabelsRule().check(p)
    assert result.severity == Severity.OK


def test_invalid_label_uppercase_fails():
    p = _FakePipeline(labels=["TeamData"])
    result = InvalidLabelFormatRule().check(p)
    assert result.severity == Severity.ERROR
    assert "TeamData" in result.message


def test_invalid_label_starts_with_number_fails():
    p = _FakePipeline(labels=["1team"])
    result = InvalidLabelFormatRule().check(p)
    assert result.severity == Severity.ERROR


def test_valid_labels_pass_format_rule():
    p = _FakePipeline(labels=["team-data", "v2", "my_pipeline"])
    result = InvalidLabelFormatRule().check(p)
    assert result.severity == Severity.OK


def test_reserved_label_returns_warning():
    p = _FakePipeline(labels=["deprecated"])
    result = ReservedLabelRule().check(p)
    assert result.severity == Severity.WARNING
    assert "deprecated" in result.message


def test_multiple_reserved_labels_returns_warning():
    p = _FakePipeline(labels=["internal", "experimental", "team-data"])
    result = ReservedLabelRule().check(p)
    assert result.severity == Severity.WARNING


def test_no_reserved_labels_passes():
    p = _FakePipeline(labels=["team-data", "finance"])
    result = ReservedLabelRule().check(p)
    assert result.severity == Severity.OK
