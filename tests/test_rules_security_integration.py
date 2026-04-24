from dataclasses import dataclass, field
from typing import Any

from pipecheck.rules.security_rules import (
    NoSecurityConfigRule,
    InvalidScanLevelRule,
    WeakAuthMethodRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FullPipeline:
    security: Any = None


def _security_rules():
    return [
        NoSecurityConfigRule(),
        InvalidScanLevelRule(),
        WeakAuthMethodRule(),
    ]


def _check_all(pipeline):
    return [rule.check(pipeline) for rule in _security_rules()]


def test_valid_security_all_pass():
    pipeline = _FullPipeline(
        security={"scan_level": "strict", "auth_method": "iam"}
    )
    results = _check_all(pipeline)
    assert all(r.passed for r in results), [
        r.message for r in results if not r.passed
    ]


def test_missing_security_produces_warning():
    pipeline = _FullPipeline(security=None)
    results = _check_all(pipeline)
    failures = [r for r in results if not r.passed]
    assert any(r.severity == Severity.WARNING for r in failures)


def test_weak_auth_produces_error():
    pipeline = _FullPipeline(
        security={"scan_level": "standard", "auth_method": "basic"}
    )
    results = _check_all(pipeline)
    failures = [r for r in results if not r.passed]
    assert any(r.severity == Severity.ERROR for r in failures)


def test_insecure_scan_level_produces_error():
    pipeline = _FullPipeline(
        security={"scan_level": "disabled", "auth_method": "oauth2"}
    )
    results = _check_all(pipeline)
    failures = [r for r in results if not r.passed]
    assert any(r.severity == Severity.ERROR for r in failures)


def test_both_issues_produce_multiple_failures():
    pipeline = _FullPipeline(
        security={"scan_level": "none", "auth_method": "anonymous"}
    )
    results = _check_all(pipeline)
    failures = [r for r in results if not r.passed]
    assert len(failures) >= 2
