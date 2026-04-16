import pytest
from dataclasses import dataclass, field
from typing import List, Optional
from pipecheck.rules import run_rules
from pipecheck.rules.label_rules import (
    NoLabelsRule,
    TooManyLabelsRule,
    InvalidLabelFormatRule,
    ReservedLabelRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FullPipeline:
    pipeline_id: str = "my_pipeline"
    name: str = "My Pipeline"
    schedule: str = "@daily"
    tags: List[str] = field(default_factory=lambda: ["team"])
    labels: Optional[List[str]] = None
    retries: int = 1
    retry_delay: int = 300
    timeout: int = 3600
    owner: str = "data-team"
    description: str = "A valid pipeline"
    owner_contact: str = "data-team@example.com"
    environment: str = "production"
    concurrency: int = 2
    alerts: List[str] = field(default_factory=lambda: ["#alerts"])
    sla: int = 7200
    dependencies: List[str] = field(default_factory=list)

    def __post_init__(self):
        pass


def test_valid_labels_all_pass():
    p = _FullPipeline(labels=["team-data", "v2"])
    rules = [NoLabelsRule(), TooManyLabelsRule(), InvalidLabelFormatRule(), ReservedLabelRule()]
    results = run_rules(p, rules=rules)
    assert all(r.severity == Severity.OK for r in results)


def test_missing_labels_produces_warning():
    p = _FullPipeline(labels=None)
    rules = [NoLabelsRule()]
    results = run_rules(p, rules=rules)
    assert any(r.severity == Severity.WARNING for r in results)


def test_reserved_and_invalid_labels_produce_failures():
    p = _FullPipeline(labels=["Deprecated", "experimental"])
    rules = [InvalidLabelFormatRule(), ReservedLabelRule()]
    results = run_rules(p, rules=rules)
    severities = {r.severity for r in results}
    assert Severity.ERROR in severities or Severity.WARNING in severities
