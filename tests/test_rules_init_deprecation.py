import pytest
from dataclasses import dataclass
from pipecheck.rules import DEFAULT_RULES, run_rules
from pipecheck.rules.deprecation_rules import (
    NoDeprecationPolicyRule,
    InvalidDeprecationDateRule,
    DeprecatedPipelineActiveRule,
    NoDeprecationOwnerRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _MinimalPipeline:
    """Pipeline with all attributes set to safe defaults for rule scanning."""
    id: str = "my_pipeline"
    name: str = "my_pipeline"
    tags: list = None
    schedule: str = "@daily"
    dependencies: list = None
    retries: int = 1
    retry_delay: int = 60
    timeout: int = 3600
    owner: str = "data-team"
    description: str = "A valid pipeline description"
    owner_contact: str = "data-team@example.com"
    environment: str = "production"
    max_active_runs: int = 1
    alerts: list = None
    sla: int = 7200
    labels: dict = None
    memory_limit: str = "2Gi"
    cpu_limit: str = "1"
    notifications: list = None
    version: str = "1.0.0"
    metadata: dict = None
    access_level: str = "internal"
    allowed_roles: list = None
    data_quality_checks: list = None
    checkpoint: str = "enabled"
    checkpoint_interval: int = 100
    lineage: dict = None
    trigger: str = "scheduled"
    cost_estimate: float = 1.0
    cost_tier: str = "low"
    compliance_tag: str = "public"
    cache_strategy: str = "none"
    parallelism: int = 4
    backfill: dict = None
    idempotency: str = "insert-ignore"
    log_config: dict = None
    runtime_limit: int = 3600
    priority: str = "normal"
    encryption: str = "AES-256"
    audit: dict = None
    deprecation_policy: object = None
    active: bool = True

    def __post_init__(self):
        if self.tags is None:
            self.tags = ["team:data"]
        if self.dependencies is None:
            self.dependencies = []
        if self.alerts is None:
            self.alerts = ["#data-alerts"]
        if self.labels is None:
            self.labels = {"team": "data"}
        if self.notifications is None:
            self.notifications = [{"type": "email", "on": "failure"}]
        if self.allowed_roles is None:
            self.allowed_roles = ["analyst"]
        if self.data_quality_checks is None:
            self.data_quality_checks = ["not_null"]
        if self.lineage is None:
            self.lineage = {"inputs": ["raw.events"], "outputs": ["clean.events"]}
        if self.backfill is None:
            self.backfill = {"strategy": "full"}
        if self.log_config is None:
            self.log_config = {"level": "INFO"}
        if self.audit is None:
            self.audit = {"level": "standard"}


def test_default_rules_include_deprecation_rules():
    rule_types = {type(r) for r in DEFAULT_RULES}
    assert NoDeprecationPolicyRule in rule_types
    assert InvalidDeprecationDateRule in rule_types
    assert DeprecatedPipelineActiveRule in rule_types
    assert NoDeprecationOwnerRule in rule_types


def test_run_rules_includes_deprecation_results():
    pipeline = _MinimalPipeline()
    results = run_rules(pipeline)
    rule_names = {r.rule for r in results}
    assert "no_deprecation_policy" in rule_names
    assert "invalid_deprecation_date" in rule_names
    assert "deprecated_pipeline_active" in rule_names
    assert "no_deprecation_owner" in rule_names


def test_pipeline_with_valid_deprecation_policy_passes_all_deprecation_rules():
    pipeline = _MinimalPipeline(
        deprecation_policy={"deprecate_on": "2099-12-31", "owner": "platform-team"},
        active=True,
    )
    results = run_rules(pipeline)
    deprecation_results = [
        r for r in results
        if r.rule in {
            "no_deprecation_policy",
            "invalid_deprecation_date",
            "deprecated_pipeline_active",
            "no_deprecation_owner",
        }
    ]
    assert all(r.severity == Severity.OK for r in deprecation_results)
