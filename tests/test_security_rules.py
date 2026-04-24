import pytest
from dataclasses import dataclass, field
from typing import Any

from pipecheck.rules.security_rules import (
    NoSecurityConfigRule,
    InvalidScanLevelRule,
    WeakAuthMethodRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FakePipeline:
    security: Any = None


# --- NoSecurityConfigRule ---

def test_no_security_returns_warning():
    result = NoSecurityConfigRule().check(_FakePipeline())
    assert not result.passed
    assert result.severity == Severity.WARNING


def test_empty_dict_security_returns_warning():
    result = NoSecurityConfigRule().check(_FakePipeline(security={}))
    assert not result.passed


def test_security_present_passes_no_security_rule():
    result = NoSecurityConfigRule().check(
        _FakePipeline(security={"scan_level": "standard"})
    )
    assert result.passed


def test_security_string_passes_no_security_rule():
    result = NoSecurityConfigRule().check(_FakePipeline(security="strict"))
    assert result.passed


# --- InvalidScanLevelRule ---

def test_no_security_passes_invalid_scan_rule():
    result = InvalidScanLevelRule().check(_FakePipeline())
    assert result.passed


def test_non_dict_security_passes_invalid_scan_rule():
    result = InvalidScanLevelRule().check(_FakePipeline(security="strict"))
    assert result.passed


def test_no_scan_level_key_passes_invalid_scan_rule():
    result = InvalidScanLevelRule().check(_FakePipeline(security={"auth_method": "iam"}))
    assert result.passed


@pytest.mark.parametrize("level", ["basic", "standard", "strict"])
def test_valid_scan_levels_pass(level):
    result = InvalidScanLevelRule().check(
        _FakePipeline(security={"scan_level": level})
    )
    assert result.passed


@pytest.mark.parametrize("level", ["none", "disabled", "off"])
def test_insecure_scan_levels_return_error(level):
    result = InvalidScanLevelRule().check(
        _FakePipeline(security={"scan_level": level})
    )
    assert not result.passed
    assert result.severity == Severity.ERROR
    assert level in result.message


def test_unknown_scan_level_returns_error():
    result = InvalidScanLevelRule().check(
        _FakePipeline(security={"scan_level": "super_strict"})
    )
    assert not result.passed
    assert "super_strict" in result.message


# --- WeakAuthMethodRule ---

def test_no_security_passes_weak_auth_rule():
    result = WeakAuthMethodRule().check(_FakePipeline())
    assert result.passed


def test_no_auth_method_key_passes_weak_auth_rule():
    result = WeakAuthMethodRule().check(
        _FakePipeline(security={"scan_level": "strict"})
    )
    assert result.passed


@pytest.mark.parametrize(
    "method", ["iam", "oauth2", "api_key", "service_account", "mtls"]
)
def test_valid_auth_methods_pass(method):
    result = WeakAuthMethodRule().check(
        _FakePipeline(security={"auth_method": method})
    )
    assert result.passed


@pytest.mark.parametrize("method", ["basic", "none", "anonymous"])
def test_weak_auth_methods_return_error(method):
    result = WeakAuthMethodRule().check(
        _FakePipeline(security={"auth_method": method})
    )
    assert not result.passed
    assert result.severity == Severity.ERROR
    assert method in result.message
