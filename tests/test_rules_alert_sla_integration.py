import pytest
from dataclasses import dataclass, field
from typing import Optional, List
from pipecheck.rules import run_rules
from pipecheck.rules.alert_rules import NoAlertRule, InvalidAlertChannelRule, TooManyAlertsRule
from pipecheck.rules.sla_rules import NoSLARule, SLATooLongRule, ZeroSLARule


@dataclass
class _FullPipeline:
    id: str = "my_pipeline"
    name: str = "my_pipeline"
    tags: List[str] = field(default_factory=lambda: ["team:data"])
    schedule: Optional[str] = "0 * * * *"
    retries: Optional[int] = 2
    retry_delay: Optional[int] = 300
    timeout: Optional[int] = 3600
    owner: Optional[str] = "data-team"
    description: Optional[str] = "A well-documented pipeline."
    owner_contact: Optional[str] = "data-team@example.com"
    environment: Optional[str] = "production"
    concurrency: Optional[int] = 3
    dependencies: Optional[List[str]] = field(default_factory=lambda: ["upstream_pipeline"])
    alerts: Optional[List[str]] = field(default_factory=lambda: ["slack"])
    sla: Optional[int] = 3600

    def __post_init__(self):
        pass


def test_alert_rules_run_and_pass_for_valid_pipeline():
    p = _FullPipeline()
    rules = [NoAlertRule(), InvalidAlertChannelRule(), TooManyAlertsRule()]
    results = run_rules(p, rules=rules)
    assert all(r.passed for r in results)


def test_sla_rules_run_and_pass_for_valid_pipeline():
    p = _FullPipeline()
    rules = [NoSLARule(), SLATooLongRule(), ZeroSLARule()]
    results = run_rules(p, rules=rules)
    assert all(r.passed for r in results)


def test_missing_alerts_and_sla_produces_failures():
    p = _FullPipeline(alerts=None, sla=None)
    rules = [NoAlertRule(), NoSLARule()]
    results = run_rules(p, rules=rules)
    assert all(not r.passed for r in results)


def test_invalid_alert_channel_and_zero_sla_produce_errors():
    p = _FullPipeline(alerts=["discord"], sla=0)
    rules = [InvalidAlertChannelRule(), ZeroSLARule()]
    results = run_rules(p, rules=rules)
    assert all(not r.passed for r in results)
