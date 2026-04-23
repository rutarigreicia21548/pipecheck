from dataclasses import dataclass, field
from typing import Any

from pipecheck.rules import run_rules
from pipecheck.rules.rollback_rules import (
    NoRollbackConfigRule,
    InvalidRollbackStrategyRule,
    RollbackWindowTooLargeRule,
)


@dataclass
class _MinimalPipeline:
    pipeline_id: str = "test_pipeline"
    name: str = "Test Pipeline"
    schedule: str = "@daily"
    tags: list = field(default_factory=lambda: ["team:eng"])
    owner: str = "eng-team"
    description: str = "A test pipeline."
    environment: str = "production"
    retries: int = 2
    retry_delay: int = 300
    timeout: int = 3600
    concurrency: int = 4
    dependencies: list = field(default_factory=list)
    rollback: Any = None

    def __post_init__(self):
        # satisfy any attribute lookups for rules not under test
        pass


def test_default_rules_include_rollback_rules():
    from pipecheck.rules import DEFAULT_RULES
    rule_types = {type(r) for r in DEFAULT_RULES}
    assert NoRollbackConfigRule in rule_types
    assert InvalidRollbackStrategyRule in rule_types
    assert RollbackWindowTooLargeRule in rule_types


def test_run_rules_includes_rollback_results():
    pipeline = _MinimalPipeline(rollback={"strategy": "full", "window_days": 7})
    results = run_rules(pipeline)
    rule_names = {r.rule for r in results}
    assert "no-rollback-config" in rule_names
    assert "invalid-rollback-strategy" in rule_names
    assert "rollback-window-too-large" in rule_names


def test_pipeline_with_valid_rollback_passes_all_rollback_rules():
    pipeline = _MinimalPipeline(
        rollback={"strategy": "checkpoint", "window_days": 10}
    )
    results = run_rules(pipeline)
    rollback_results = [
        r for r in results
        if r.rule in {
            "no-rollback-config",
            "invalid-rollback-strategy",
            "rollback-window-too-large",
        }
    ]
    assert rollback_results, "Expected rollback rule results"
    assert all(r.passed for r in rollback_results), [
        r.message for r in rollback_results if not r.passed
    ]
