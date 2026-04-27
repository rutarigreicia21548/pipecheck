import pytest
from dataclasses import dataclass, field
from typing import Any, Optional

from pipecheck.rules.isolation_rules import (
    NoIsolationConfigRule,
    InvalidIsolationLevelRule,
    InsecureIsolationLevelRule,
    TooManySharedResourcesRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FakePipeline:
    isolation: Optional[Any] = None


# --- NoIsolationConfigRule ---

def test_no_isolation_returns_warning():
    p = _FakePipeline()
    result = NoIsolationConfigRule().check(p)
    assert result.severity == Severity.WARNING


def test_empty_dict_isolation_returns_warning():
    p = _FakePipeline(isolation={})
    result = NoIsolationConfigRule().check(p)
    assert result.severity == Severity.WARNING


def test_isolation_present_passes_no_isolation_rule():
    p = _FakePipeline(isolation={"level": "container"})
    result = NoIsolationConfigRule().check(p)
    assert result.severity == Severity.OK


# --- InvalidIsolationLevelRule ---

def test_no_isolation_passes_invalid_level_rule():
    p = _FakePipeline()
    result = InvalidIsolationLevelRule().check(p)
    assert result.severity == Severity.OK


def test_valid_isolation_levels_pass():
    for level in ("none", "process", "container", "vm", "sandbox"):
        p = _FakePipeline(isolation={"level": level})
        result = InvalidIsolationLevelRule().check(p)
        assert result.severity == Severity.OK, f"Expected OK for level={level}"


def test_invalid_isolation_level_returns_error():
    p = _FakePipeline(isolation={"level": "hypervisor"})
    result = InvalidIsolationLevelRule().check(p)
    assert result.severity == Severity.ERROR
    assert "hypervisor" in result.message


def test_missing_level_key_passes_invalid_rule():
    p = _FakePipeline(isolation={"shared_resources": []})
    result = InvalidIsolationLevelRule().check(p)
    assert result.severity == Severity.OK


# --- InsecureIsolationLevelRule ---

def test_no_isolation_passes_insecure_rule():
    p = _FakePipeline()
    result = InsecureIsolationLevelRule().check(p)
    assert result.severity == Severity.OK


def test_none_level_returns_warning():
    p = _FakePipeline(isolation={"level": "none"})
    result = InsecureIsolationLevelRule().check(p)
    assert result.severity == Severity.WARNING


def test_secure_levels_pass_insecure_rule():
    for level in ("process", "container", "vm", "sandbox"):
        p = _FakePipeline(isolation={"level": level})
        result = InsecureIsolationLevelRule().check(p)
        assert result.severity == Severity.OK, f"Expected OK for level={level}"


# --- TooManySharedResourcesRule ---

def test_no_isolation_passes_shared_resources_rule():
    p = _FakePipeline()
    result = TooManySharedResourcesRule().check(p)
    assert result.severity == Severity.OK


def test_shared_resources_within_limit_passes():
    p = _FakePipeline(isolation={"level": "container", "shared_resources": ["db", "cache"]})
    result = TooManySharedResourcesRule().check(p)
    assert result.severity == Severity.OK


def test_too_many_shared_resources_returns_warning():
    resources = [f"res_{i}" for i in range(11)]
    p = _FakePipeline(isolation={"level": "container", "shared_resources": resources})
    result = TooManySharedResourcesRule().check(p)
    assert result.severity == Severity.WARNING
    assert "11" in result.message


def test_exactly_at_limit_passes_shared_resources_rule():
    resources = [f"res_{i}" for i in range(10)]
    p = _FakePipeline(isolation={"level": "container", "shared_resources": resources})
    result = TooManySharedResourcesRule().check(p)
    assert result.severity == Severity.OK
