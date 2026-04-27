from dataclasses import dataclass, field
from typing import Any, Optional

from pipecheck.rules.isolation_rules import (
    NoIsolationConfigRule,
    InvalidIsolationLevelRule,
    InsecureIsolationLevelRule,
    TooManySharedResourcesRule,
)
from pipecheck.rules.base import Severity


_ISOLATION_RULES = [
    NoIsolationConfigRule(),
    InvalidIsolationLevelRule(),
    InsecureIsolationLevelRule(),
    TooManySharedResourcesRule(),
]


@dataclass
class _FullPipeline:
    isolation: Optional[Any] = None


def _run(pipeline):
    return [rule.check(pipeline) for rule in _ISOLATION_RULES]


def test_valid_container_isolation_all_pass():
    p = _FullPipeline(isolation={"level": "container", "shared_resources": ["logging"]})
    results = _run(p)
    assert all(r.severity == Severity.OK for r in results), [
        (r.rule, r.severity, r.message) for r in results if r.severity != Severity.OK
    ]


def test_missing_isolation_produces_warning():
    p = _FullPipeline()
    results = _run(p)
    warnings = [r for r in results if r.severity == Severity.WARNING]
    assert any(r.rule == "no_isolation_config" for r in warnings)


def test_invalid_level_produces_error():
    p = _FullPipeline(isolation={"level": "chroot"})
    results = _run(p)
    errors = [r for r in results if r.severity == Severity.ERROR]
    assert any(r.rule == "invalid_isolation_level" for r in errors)


def test_none_level_produces_warning():
    p = _FullPipeline(isolation={"level": "none"})
    results = _run(p)
    warnings = [r for r in results if r.severity == Severity.WARNING]
    assert any(r.rule == "insecure_isolation_level" for r in warnings)


def test_excessive_shared_resources_produces_warning():
    resources = [f"svc_{i}" for i in range(15)]
    p = _FullPipeline(isolation={"level": "vm", "shared_resources": resources})
    results = _run(p)
    warnings = [r for r in results if r.severity == Severity.WARNING]
    assert any(r.rule == "too_many_shared_resources" for r in warnings)
