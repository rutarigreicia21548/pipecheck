from dataclasses import dataclass, field
from typing import Any, Optional

from pipecheck.rules import run_rules
from pipecheck.rules.isolation_rules import (
    NoIsolationConfigRule,
    InvalidIsolationLevelRule,
    InsecureIsolationLevelRule,
    TooManySharedResourcesRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _MinimalPipeline:
    id: str = "my_pipeline"
    name: str = "my_pipeline"
    schedule: str = "@daily"
    tags: list = field(default_factory=lambda: ["team:data"])
    owner: str = "data-team"
    retries: int = 1
    timeout: int = 3600
    concurrency: int = 2
    description: str = "A test pipeline."
    environment: str = "production"
    alerts: list = field(default_factory=lambda: ["#alerts"])
    sla: int = 7200
    labels: dict = field(default_factory=lambda: {"team": "data"})
    memory_limit: str = "512Mi"
    cpu_limit: str = "500m"
    isolation: Optional[Any] = None

    def __post_init__(self):
        # satisfy any attribute checks in other rules
        pass


def test_default_rules_include_isolation_rules():
    from pipecheck.rules import DEFAULT_RULES
    rule_types = {type(r) for r in DEFAULT_RULES}
    assert NoIsolationConfigRule in rule_types
    assert InvalidIsolationLevelRule in rule_types
    assert InsecureIsolationLevelRule in rule_types
    assert TooManySharedResourcesRule in rule_types


def test_run_rules_includes_isolation_results():
    p = _MinimalPipeline(isolation={"level": "container"})
    results = run_rules(p)
    rule_names = {r.rule for r in results}
    assert "no_isolation_config" in rule_names
    assert "invalid_isolation_level" in rule_names


def test_pipeline_with_valid_isolation_passes_all_isolation_rules():
    p = _MinimalPipeline(
        isolation={"level": "container", "shared_resources": ["logging", "metrics"]}
    )
    results = run_rules(p)
    isolation_results = [
        r for r in results
        if r.rule in {
            "no_isolation_config",
            "invalid_isolation_level",
            "insecure_isolation_level",
            "too_many_shared_resources",
        }
    ]
    failures = [r for r in isolation_results if r.severity not in (Severity.OK, Severity.WARNING)]
    assert failures == [], failures
