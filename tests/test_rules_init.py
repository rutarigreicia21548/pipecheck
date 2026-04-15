import pytest
from dataclasses import dataclass
from typing import Optional, List
from pipecheck.rules import run_rules, DEFAULT_RULES
from pipecheck.rules.retries_rules import NoRetriesRule, TooManyRetriesRule, NoRetryDelayRule


@dataclass
class _FullPipeline:
    id: str = "my_pipeline"
    name: Optional[str] = None
    schedule: Optional[str] = "@daily"
    tags: List[str] = None
    dependencies: List[str] = None
    retries: Optional[int] = 3
    retry_delay: Optional[int] = 300

    def __post_init__(self):
        if self.tags is None:
            self.tags = ["team_data"]
        if self.dependencies is None:
            self.dependencies = []


def test_default_rules_include_retries_rules():
    rule_names = [r.name for r in DEFAULT_RULES]
    assert "no-retries" in rule_names
    assert "too-many-retries" in rule_names
    assert "no-retry-delay" in rule_names


def test_run_rules_returns_results_for_each_rule():
    pipeline = _FullPipeline()
    results = run_rules(pipeline)
    assert len(results) == len(DEFAULT_RULES)


def test_run_rules_with_custom_rules():
    pipeline = _FullPipeline(retries=None)
    results = run_rules(pipeline, rules=[NoRetriesRule()])
    assert len(results) == 1
    assert not results[0].passed


def test_run_rules_all_pass_for_well_configured_pipeline():
    pipeline = _FullPipeline()
    results = run_rules(
        pipeline,
        rules=[NoRetriesRule(), TooManyRetriesRule(), NoRetryDelayRule()],
    )
    assert all(r.passed for r in results)


def test_run_rules_collects_failures():
    pipeline = _FullPipeline(retries=10, retry_delay=None)
    results = run_rules(
        pipeline,
        rules=[TooManyRetriesRule(), NoRetryDelayRule()],
    )
    failed = [r for r in results if not r.passed]
    assert len(failed) == 2
