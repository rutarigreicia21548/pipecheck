import pytest
from dataclasses import dataclass, field
from typing import Optional, List
from pipecheck.rules import run_rules
from pipecheck.rules.resource_rules import DEFAULT_RESOURCE_RULES
from pipecheck.rules.base import Severity


@dataclass
class _FullPipeline:
    pipeline_id: str = "my_pipeline"
    tags: List[str] = field(default_factory=lambda: ["team:data"])
    schedule: str = "@daily"
    retries: int = 2
    retry_delay: int = 300
    timeout: int = 3600
    owner: str = "data-team"
    description: str = "Integration test pipeline"
    owner_contact: str = "data-team@example.com"
    environment: str = "production"
    concurrency: int = 4
    alerts: List[str] = field(default_factory=lambda: ["#alerts"])
    sla: int = 7200
    labels: dict = field(default_factory=lambda: {"team": "data"})
    memory_limit: Optional[int] = None
    cpu_limit: Optional[float] = None


def test_valid_resources_all_pass():
    p = _FullPipeline(memory_limit=1024, cpu_limit=4)
    results = run_rules(p, rules=DEFAULT_RESOURCE_RULES)
    assert all(r.severity == Severity.OK for r in results)


def test_missing_resources_produces_warnings():
    p = _FullPipeline()
    results = run_rules(p, rules=DEFAULT_RESOURCE_RULES)
    severities = {r.rule: r.severity for r in results}
    assert severities["no_memory_limit"] == Severity.WARNING
    assert severities["no_cpu_limit"] == Severity.WARNING


def test_excessive_resources_produce_errors():
    p = _FullPipeline(memory_limit=99999, cpu_limit=100)
    results = run_rules(p, rules=DEFAULT_RESOURCE_RULES)
    severities = {r.rule: r.severity for r in results}
    assert severities["memory_limit_too_high"] == Severity.ERROR
    assert severities["cpu_limit_too_high"] == Severity.ERROR
