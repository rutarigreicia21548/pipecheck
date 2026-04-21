from dataclasses import dataclass, field
from typing import Any

from pipecheck.rules.audit_rules import (
    NoAuditConfigRule,
    InvalidAuditLevelRule,
    AuditRetentionTooLongRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FullPipeline:
    pipeline_id: str = "my_pipeline"
    schedule: str = "@daily"
    tags: list = field(default_factory=lambda: ["team:data"])
    audit: Any = None


def _audit_rules():
    return [NoAuditConfigRule(), InvalidAuditLevelRule(), AuditRetentionTooLongRule()]


def test_valid_audit_all_pass():
    pipeline = _FullPipeline(audit={"level": "full", "retention_days": 180})
    results = [rule.check(pipeline) for rule in _audit_rules()]
    severities = {r.severity for r in results}
    assert severities == {Severity.OK}


def test_missing_audit_produces_warning():
    pipeline = _FullPipeline(audit=None)
    results = [rule.check(pipeline) for rule in _audit_rules()]
    warnings = [r for r in results if r.severity == Severity.WARNING]
    assert len(warnings) >= 1


def test_invalid_audit_level_produces_error():
    pipeline = _FullPipeline(audit={"level": "debug", "retention_days": 30})
    results = [rule.check(pipeline) for rule in _audit_rules()]
    errors = [r for r in results if r.severity == Severity.ERROR]
    assert len(errors) >= 1


def test_excessive_retention_produces_error():
    pipeline = _FullPipeline(audit={"level": "basic", "retention_days": 999})
    results = [rule.check(pipeline) for rule in _audit_rules()]
    errors = [r for r in results if r.severity == Severity.ERROR]
    assert len(errors) >= 1


def test_audit_without_level_key_produces_warning():
    pipeline = _FullPipeline(audit={"retention_days": 60})
    results = [rule.check(pipeline) for rule in _audit_rules()]
    non_ok = [r for r in results if r.severity != Severity.OK]
    assert len(non_ok) >= 1
