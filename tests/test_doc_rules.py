import pytest
from dataclasses import dataclass, field
from pipecheck.rules.doc_rules import NoDescriptionRule, ShortDescriptionRule, NoOwnerContactRule


@dataclass
class _FakePipeline:
    description: str = None

    def __post_init__(self):
        pass


def test_no_description_returns_warning():
    p = _FakePipeline(description=None)
    result = NoDescriptionRule().check(p)
    assert not result.passed


def test_empty_description_returns_warning():
    p = _FakePipeline(description="   ")
    result = NoDescriptionRule().check(p)
    assert not result.passed


def test_description_present_passes():
    p = _FakePipeline(description="Loads daily sales data.")
    result = NoDescriptionRule().check(p)
    assert result.passed


def test_short_description_fails():
    p = _FakePipeline(description="Short")
    result = ShortDescriptionRule().check(p)
    assert not result.passed
    assert "too short" in result.message


def test_long_enough_description_passes():
    p = _FakePipeline(description="Loads daily sales data from S3.")
    result = ShortDescriptionRule().check(p)
    assert result.passed


def test_short_description_custom_min():
    p = _FakePipeline(description="Hi")
    result = ShortDescriptionRule(min_length=3).check(p)
    assert not result.passed


def test_no_description_short_rule_fails():
    p = _FakePipeline(description=None)
    result = ShortDescriptionRule().check(p)
    assert not result.passed


def test_no_contact_in_description_fails():
    p = _FakePipeline(description="Loads daily sales data from S3.")
    result = NoOwnerContactRule().check(p)
    assert not result.passed
    assert "email" in result.message


def test_contact_in_description_passes():
    p = _FakePipeline(description="Owned by team@example.com. Loads sales data.")
    result = NoOwnerContactRule().check(p)
    assert result.passed


def test_no_description_contact_rule_fails():
    p = _FakePipeline(description=None)
    result = NoOwnerContactRule().check(p)
    assert not result.passed
