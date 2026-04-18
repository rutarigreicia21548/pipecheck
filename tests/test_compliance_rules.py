import pytest
from dataclasses import dataclass, field
from typing import Optional
from pipecheck.rules.compliance_rules import (
    NoComplianceTagRule,
    InvalidComplianceTagRule,
    PiiWithoutOwnerRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FakePipeline:
    compliance_tag: Optional[str] = None
    owner: Optional[str] = None


def test_no_compliance_tag_returns_warning():
    result = NoComplianceTagRule().check(_FakePipeline())
    assert result.severity == Severity.WARNING


def test_compliance_tag_present_passes_no_compliance_rule():
    result = NoComplianceTagRule().check(_FakePipeline(compliance_tag="pii"))
    assert result.severity == Severity.OK


def test_empty_string_compliance_tag_returns_warning():
    result = NoComplianceTagRule().check(_FakePipeline(compliance_tag=""))
    assert result.severity == Severity.WARNING


def test_valid_compliance_tags_pass_invalid_rule():
    for tag in ["pii", "hipaa", "gdpr", "sox", "public", "internal"]:
        result = InvalidComplianceTagRule().check(_FakePipeline(compliance_tag=tag))
        assert result.severity == Severity.OK, f"Expected OK for tag '{tag}'"


def test_invalid_compliance_tag_returns_error():
    result = InvalidComplianceTagRule().check(_FakePipeline(compliance_tag="unknown"))
    assert result.severity == Severity.ERROR
    assert "unknown" in result.message


def test_no_tag_passes_invalid_compliance_rule():
    result = InvalidComplianceTagRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_pii_without_owner_returns_error():
    result = PiiWithoutOwnerRule().check(_FakePipeline(compliance_tag="pii", owner=None))
    assert result.severity == Severity.ERROR


def test_pii_with_owner_passes():
    result = PiiWithoutOwnerRule().check(_FakePipeline(compliance_tag="pii", owner="team@example.com"))
    assert result.severity == Severity.OK


def test_non_pii_tag_without_owner_passes_pii_rule():
    result = PiiWithoutOwnerRule().check(_FakePipeline(compliance_tag="public", owner=None))
    assert result.severity == Severity.OK


def test_no_tag_no_owner_passes_pii_rule():
    result = PiiWithoutOwnerRule().check(_FakePipeline())
    assert result.severity == Severity.OK
