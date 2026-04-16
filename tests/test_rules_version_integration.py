import pytest
from dataclasses import dataclass, field
from typing import Optional, List
from pipecheck.rules import run_rules
from pipecheck.rules.version_rules import (
    NoVersionRule,
    InvalidVersionFormatRule,
    MajorVersionZeroRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FullPipeline:
    pipeline_id: str = "my_pipeline"
    version: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    schedule: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    retries: Optional[int] = None
    timeout: Optional[int] = None
    owner: Optional[str] = None
    description: Optional[str] = None
    owner_contact: Optional[str] = None
    environment: Optional[str] = None
    concurrency: Optional[int] = None
    alerts: List[str] = field(default_factory=list)
    sla: Optional[int] = None
    labels: dict = field(default_factory=dict)
    memory_limit: Optional[int] = None
    cpu_limit: Optional[float] = None
    notifications: List[dict] = field(default_factory=list)


VERSION_RULES = [NoVersionRule(), InvalidVersionFormatRule(), MajorVersionZeroRule()]


def test_valid_version_all_pass():
    p = _FullPipeline(version="2.0.1")
    results = run_rules(p, rules=VERSION_RULES)
    assert all(r.severity == Severity.OK for r in results)


def test_missing_version_produces_warning():
    p = _FullPipeline(version=None)
    results = run_rules(p, rules=VERSION_RULES)
    severities = [r.severity for r in results]
    assert Severity.WARNING in severities


def test_invalid_format_produces_error():
    p = _FullPipeline(version="release-1")
    results = run_rules(p, rules=VERSION_RULES)
    severities = [r.severity for r in results]
    assert Severity.ERROR in severities
