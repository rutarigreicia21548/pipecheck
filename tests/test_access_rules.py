import pytest
from dataclasses import dataclass, field
from typing import Optional, List
from pipecheck.rules.base import Severity
from pipecheck.rules.access_rules import (
    NoAccessLevelRule,
    InvalidAccessLevelRule,
    NoAllowedRolesRule,
    TooManyRolesRule,
)


@dataclass
class _FakePipeline:
    access_level: Optional[str] = None
    allowed_roles: Optional[List[str]] = None


def test_no_access_level_returns_warning():
    p = _FakePipeline()
    result = NoAccessLevelRule().check(p)
    assert result.severity == Severity.WARNING


def test_access_level_present_passes_no_access_rule():
    p = _FakePipeline(access_level="public")
    result = NoAccessLevelRule().check(p)
    assert result.severity == Severity.OK


def test_valid_access_levels_pass_invalid_rule():
    for level in ("public", "internal", "restricted", "private"):
        p = _FakePipeline(access_level=level)
        result = InvalidAccessLevelRule().check(p)
        assert result.severity == Severity.OK, f"Expected OK for level '{level}'"


def test_invalid_access_level_returns_error():
    p = _FakePipeline(access_level="open")
    result = InvalidAccessLevelRule().check(p)
    assert result.severity == Severity.ERROR
    assert "open" in result.message


def test_no_access_level_skips_invalid_rule():
    p = _FakePipeline(access_level=None)
    result = InvalidAccessLevelRule().check(p)
    assert result.severity == Severity.OK


def test_restricted_without_roles_returns_error():
    p = _FakePipeline(access_level="restricted")
    result = NoAllowedRolesRule().check(p)
    assert result.severity == Severity.ERROR


def test_private_without_roles_returns_error():
    p = _FakePipeline(access_level="private")
    result = NoAllowedRolesRule().check(p)
    assert result.severity == Severity.ERROR


def test_restricted_with_roles_passes():
    p = _FakePipeline(access_level="restricted", allowed_roles=["data-eng"])
    result = NoAllowedRolesRule().check(p)
    assert result.severity == Severity.OK


def test_public_without_roles_passes_no_allowed_roles_rule():
    p = _FakePipeline(access_level="public")
    result = NoAllowedRolesRule().check(p)
    assert result.severity == Severity.OK


def test_roles_within_limit_passes_too_many_rule():
    p = _FakePipeline(allowed_roles=[f"role-{i}" for i in range(5)])
    result = TooManyRolesRule().check(p)
    assert result.severity == Severity.OK


def test_too_many_roles_returns_warning():
    p = _FakePipeline(allowed_roles=[f"role-{i}" for i in range(15)])
    result = TooManyRolesRule().check(p)
    assert result.severity == Severity.WARNING
    assert "15" in result.message


def test_no_roles_skips_too_many_rule():
    p = _FakePipeline()
    result = TooManyRolesRule().check(p)
    assert result.severity == Severity.OK
