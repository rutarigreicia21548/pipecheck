import pytest
from dataclasses import dataclass, field
from typing import Any, Optional

from pipecheck.rules import run_rules
from pipecheck.rules.windowing_rules import (
    NoWindowingConfigRule,
    InvalidWindowTypeRule,
    WindowSizeTooLargeRule,
    InvalidWindowUnitRule,
)


@dataclass
class _MinimalPipeline:
    pipeline_id: str = "my_pipeline"
    name: str = "my_pipeline"
    schedule: Optional[str] = "@daily"
    tags: list = field(default_factory=lambda: ["team:data"])
    owner: str = "data-team"
    retries: int = 1
    windowing: Any = None

    def __post_init__(self):
        for attr in (
            "description", "timeout", "concurrency", "environment", "alerts",
            "sla", "labels", "memory_limit", "cpu_limit", "notifications",
            "version", "metadata", "access_level", "allowed_roles",
            "data_quality_checks", "checkpoint", "lineage", "trigger",
            "cost_estimate", "cost_tier", "compliance_tag", "cache_strategy",
            "parallelism", "backfill", "idempotency", "log_config",
            "runtime_limit", "priority", "encryption", "audit",
            "deprecation_policy", "secrets", "rollback", "observability",
            "runbook", "changelog", "freshness", "rate_limit", "security",
            "storage", "health", "network", "dependencies",
        ):
            if not hasattr(self, attr):
                object.__setattr__(self, attr, None)


def test_default_rules_include_windowing_rules():
    from pipecheck.rules import DEFAULT_RULES
    rule_types = {type(r) for r in DEFAULT_RULES}
    assert NoWindowingConfigRule in rule_types
    assert InvalidWindowTypeRule in rule_types
    assert WindowSizeTooLargeRule in rule_types
    assert InvalidWindowUnitRule in rule_types


def test_run_rules_includes_windowing_results():
    pipeline = _MinimalPipeline()
    results = run_rules(pipeline)
    rule_names = {r.rule for r in results}
    assert "no_windowing_config" in rule_names
    assert "invalid_window_type" in rule_names


def test_pipeline_with_valid_windowing_passes_all_windowing_rules():
    pipeline = _MinimalPipeline(
        windowing={"type": "tumbling", "size": 15, "unit": "minutes"}
    )
    results = run_rules(pipeline)
    windowing_results = [
        r for r in results
        if r.rule in {"no_windowing_config", "invalid_window_type", "window_size_too_large", "invalid_window_unit"}
    ]
    assert all(r.passed for r in windowing_results), [r.message for r in windowing_results if not r.passed]
