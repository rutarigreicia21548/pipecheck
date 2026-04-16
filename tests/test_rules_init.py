import pytest
from dataclasses import dataclass, field
from typing import Optional, List
from pipecheck.rules import run_rules, DEFAULT_RULES
from pipecheck.rules.concurrency_rules import NoConcurrencyLimitRule
from pipecheck.rules.base import LintResult, Severity


@dataclass
class _FullPipeline:
    dag_id: str = "my_pipeline"
    name: str = "my_pipeline"
    schedule: str = "@daily"
    tags: List[str] = field(default_factory=lambda: ["team_a"])
    dependencies: List[str] = field(default_factory=list)
    retries: int = 1
    retry_delay: int = 300
    timeout: int = 3600
    owner: str = "data-team"
    description: str = "A well-documented pipeline for testing purposes"
    owner_contact: str = "data-team@example.com"
    environment: str = "production"
    concurrency: int = 8

    def __post_init__(self):
        pass


def test_default_rules_include_retries_rules():
    from pipecheck.rules.retries_rules import NoRetriesRule
    assert any(isinstance(r, NoRetriesRule) for r in DEFAULT_RULES)


def test_default_rules_include_concurrency_rules():
    assert any(isinstance(r, NoConcurrencyLimitRule) for r in DEFAULT_RULES)


def test_run_rules_returns_results_for_each_rule():
    p = _FullPipeline()
    results = run_rules(p)
    assert len(results) == len(DEFAULT_RULES)
    assert all(isinstance(r, LintResult) for r in results)


def test_run_rules_with_custom_rules():
    p = _FullPipeline()
    custom = [NoConcurrencyLimitRule()]
    results = run_rules(p, rules=custom)
    assert len(results) == 1
    assert results[0].passed


def test_run_rules_no_concurrency_fails():
    p = _FullPipeline(concurrency=None)
    custom = [NoConcurrencyLimitRule()]
    results = run_rules(p, rules=custom)
    assert not results[0].passed
