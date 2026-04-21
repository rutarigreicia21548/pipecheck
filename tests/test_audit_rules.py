import pytest
from dataclasses import dataclass, field
from typing import Any

from pipecheck.rules.audit_rules import (
    NoAuditConfigRule,
    InvalidAuditLevelRule,
    AuditRetentionTooLongRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FakePipeline:
    audit: Any = None


# --- NoAuditConfigRule ---

def test_no_audit_returns_warning():
    result = NoAuditConfigRule().check(_FakePipeline())
    assert result.severity == Severity.WARNING


def test_empty_dict_audit_returns_warning():
    result = NoAuditConfigRule().check(_FakePipeline(audit={}))
    assert result.severity == Severity.WARNING


def test_audit_present_passes_no_audit_rule():
    result = NoAuditConfigRule().check(_FakePipeline(audit={"level": "basic"}))
    assert result.severity == Severity.OK


def test_audit_string_passes_no_audit_rule():
    result = NoAuditConfigRule().check(_FakePipeline(audit="full"))
    assert result.severity == Severity.OK


# --- InvalidAuditLevelRule ---

def test_non_dict_audit_passes_invalid_level_rule():
    result = InvalidAuditLevelRule().check(_FakePipeline(audit="full"))
    assert result.severity == Severity.OK


def test_no_audit_passes_invalid_level_rule():
    result = InvalidAuditLevelRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_missing_level_key_returns_warning():
    result = InvalidAuditLevelRule().check(_FakePipeline(audit={"retention_days": 30}))
    assert result.severity == Severity.WARNING


@pytest.mark.parametrize("level", ["none", "basic", "full", "compliance"])
def test_valid_audit_levels_pass(level):
    result = InvalidAuditLevelRule().check(_FakePipeline(audit={"level": level}))
    assert result.severity == Severity.OK


def test_invalid_audit_level_returns_error():
    result = InvalidAuditLevelRule().check(_FakePipeline(audit={"level": "verbose"}))
    assert result.severity == Severity.ERROR
    assert "verbose" in result.message


# --- AuditRetentionTooLongRule ---

def test_no_audit_passes_retention_rule():
    result = AuditRetentionTooLongRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_non_dict_audit_passes_retention_rule():
    result = AuditRetentionTooLongRule().check(_FakePipeline(audit="basic"))
    assert result.severity == Severity.OK


def test_no_retention_days_passes_retention_rule():
    result = AuditRetentionTooLongRule().check(_FakePipeline(audit={"level": "full"}))
    assert result.severity == Severity.OK


def test_retention_within_limit_passes():
    result = AuditRetentionTooLongRule().check(_FakePipeline(audit={"retention_days": 90}))
    assert result.severity == Severity.OK


def test_retention_at_limit_passes():
    result = AuditRetentionTooLongRule().check(_FakePipeline(audit={"retention_days": 365}))
    assert result.severity == Severity.OK


def test_retention_too_long_returns_error():
    result = AuditRetentionTooLongRule().check(_FakePipeline(audit={"retention_days": 400}))
    assert result.severity == Severity.ERROR
    assert "400" in result.message


def test_zero_retention_returns_error():
    result = AuditRetentionTooLongRule().check(_FakePipeline(audit={"retention_days": 0}))
    assert result.severity == Severity.ERROR


def test_negative_retention_returns_error():
    result = AuditRetentionTooLongRule().check(_FakePipeline(audit={"retention_days": -5}))
    assert result.severity == Severity.ERROR
