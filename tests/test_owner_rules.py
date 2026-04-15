import pytest
from dataclasses import dataclass, field
from typing import Optional
from pipecheck.rules.owner_rules import NoOwnerRule, InvalidOwnerFormatRule, GenericOwnerRule
from pipecheck.rules.base import Severity


@dataclass
class _FakePipeline:
    pipeline_id: str = "my_pipeline"
    owner: Optional[str] = None

    def __post_init__(self):
        pass


# --- NoOwnerRule ---

def test_no_owner_returns_warning():
    rule = NoOwnerRule()
    result = rule.check(_FakePipeline(owner=None))
    assert not result.passed
    assert result.severity == Severity.WARNING


def test_empty_string_owner_returns_warning():
    rule = NoOwnerRule()
    result = rule.check(_FakePipeline(owner=""))
    assert not result.passed


def test_owner_present_passes_no_owner_rule():
    rule = NoOwnerRule()
    result = rule.check(_FakePipeline(owner="data-team"))
    assert result.passed


# --- InvalidOwnerFormatRule ---

def test_valid_owner_passes_format_rule():
    rule = InvalidOwnerFormatRule()
    for owner in ["data-team", "alice", "Bob Smith", "ops@company.com", "team_123"]:
        result = rule.check(_FakePipeline(owner=owner))
        assert result.passed, f"Expected pass for owner: {owner!r}"


def test_no_owner_passes_format_rule():
    rule = InvalidOwnerFormatRule()
    result = rule.check(_FakePipeline(owner=None))
    assert result.passed


def test_owner_with_special_chars_fails_format_rule():
    rule = InvalidOwnerFormatRule()
    result = rule.check(_FakePipeline(owner="bad!owner#"))
    assert not result.passed
    assert result.severity == Severity.ERROR
    assert "invalid characters" in result.message


def test_whitespace_only_owner_fails_format_rule():
    rule = InvalidOwnerFormatRule()
    result = rule.check(_FakePipeline(owner="   "))
    assert not result.passed


# --- GenericOwnerRule ---

@pytest.mark.parametrize("owner", ["airflow", "Airflow", "AIRFLOW", "admin", "default", "unknown", "user", "owner", "prefect"])
def test_generic_owner_fails(owner):
    rule = GenericOwnerRule()
    result = rule.check(_FakePipeline(owner=owner))
    assert not result.passed
    assert result.severity == Severity.WARNING
    assert "generic" in result.message


def test_real_owner_passes_generic_rule():
    rule = GenericOwnerRule()
    result = rule.check(_FakePipeline(owner="data-engineering"))
    assert result.passed


def test_no_owner_passes_generic_rule():
    rule = GenericOwnerRule()
    result = rule.check(_FakePipeline(owner=None))
    assert result.passed
