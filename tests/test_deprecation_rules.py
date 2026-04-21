import pytest
from dataclasses import dataclass, field
from typing import Any
from pipecheck.rules.deprecation_rules import (
    NoDeprecationPolicyRule,
    InvalidDeprecationDateRule,
    DeprecatedPipelineActiveRule,
    NoDeprecationOwnerRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FakePipeline:
    deprecation_policy: Any = None
    active: bool = True


# --- NoDeprecationPolicyRule ---

def test_no_deprecation_policy_returns_warning():
    result = NoDeprecationPolicyRule().check(_FakePipeline())
    assert result.severity == Severity.WARNING


def test_deprecation_policy_dict_passes_no_policy_rule():
    result = NoDeprecationPolicyRule().check(_FakePipeline(deprecation_policy={"deprecate_on": "2030-01-01"}))
    assert result.severity == Severity.OK


def test_deprecation_policy_string_passes_no_policy_rule():
    result = NoDeprecationPolicyRule().check(_FakePipeline(deprecation_policy="none"))
    assert result.severity == Severity.OK


# --- InvalidDeprecationDateRule ---

def test_no_policy_passes_invalid_date_rule():
    result = InvalidDeprecationDateRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_policy_string_passes_invalid_date_rule():
    result = InvalidDeprecationDateRule().check(_FakePipeline(deprecation_policy="none"))
    assert result.severity == Severity.OK


def test_valid_iso_date_passes():
    result = InvalidDeprecationDateRule().check(_FakePipeline(deprecation_policy={"deprecate_on": "2030-06-15"}))
    assert result.severity == Severity.OK


def test_invalid_date_returns_error():
    result = InvalidDeprecationDateRule().check(_FakePipeline(deprecation_policy={"deprecate_on": "not-a-date"}))
    assert result.severity == Severity.ERROR
    assert "not-a-date" in result.message


def test_no_date_key_passes_invalid_date_rule():
    result = InvalidDeprecationDateRule().check(_FakePipeline(deprecation_policy={"owner": "team"}))
    assert result.severity == Severity.OK


# --- DeprecatedPipelineActiveRule ---

def test_no_policy_passes_active_rule():
    result = DeprecatedPipelineActiveRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_future_deprecation_date_passes():
    result = DeprecatedPipelineActiveRule().check(
        _FakePipeline(deprecation_policy={"deprecate_on": "2099-12-31"}, active=True)
    )
    assert result.severity == Severity.OK


def test_past_deprecation_date_active_returns_error():
    result = DeprecatedPipelineActiveRule().check(
        _FakePipeline(deprecation_policy={"deprecate_on": "2000-01-01"}, active=True)
    )
    assert result.severity == Severity.ERROR
    assert "2000-01-01" in result.message


def test_past_deprecation_date_inactive_passes():
    result = DeprecatedPipelineActiveRule().check(
        _FakePipeline(deprecation_policy={"deprecate_on": "2000-01-01"}, active=False)
    )
    assert result.severity == Severity.OK


# --- NoDeprecationOwnerRule ---

def test_no_policy_passes_owner_rule():
    result = NoDeprecationOwnerRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_policy_with_owner_passes():
    result = NoDeprecationOwnerRule().check(_FakePipeline(deprecation_policy={"owner": "data-team"}))
    assert result.severity == Severity.OK


def test_policy_without_owner_returns_warning():
    result = NoDeprecationOwnerRule().check(_FakePipeline(deprecation_policy={"deprecate_on": "2030-01-01"}))
    assert result.severity == Severity.WARNING


def test_policy_with_empty_owner_returns_warning():
    result = NoDeprecationOwnerRule().check(_FakePipeline(deprecation_policy={"owner": "   "}))
    assert result.severity == Severity.WARNING
