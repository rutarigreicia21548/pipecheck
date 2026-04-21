from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pipecheck.rules import run_rules
from pipecheck.rules.base import Severity
from pipecheck.rules.secrets_rules import (
    InsecureSecretBackendRule,
    InvalidSecretBackendRule,
    NoSecretsConfigRule,
)


@dataclass
class _MinimalPipeline:
    """Pipeline with all required fields to avoid unrelated failures."""
    id: str = "my_pipeline"
    name: str = "my_pipeline"
    tags: list = field(default_factory=lambda: ["team:data"])
    schedule: str = "@daily"
    owner: str = "data-team@example.com"
    description: str = "A sufficiently long description for the pipeline."
    environment: str = "production"
    secrets: Any = None

    def __post_init__(self):
        # Satisfy attributes accessed by various rules
        for attr in (
            "retries", "retry_delay", "timeout", "concurrency", "alerts", "sla",
            "labels", "memory_limit", "cpu_limit", "notifications", "version",
            "metadata", "access_level", "allowed_roles", "data_quality_checks",
            "checkpoint", "lineage", "trigger", "cost_estimate", "cost_tier",
            "compliance_tag", "cache_strategy", "cache_ttl", "parallelism",
            "backfill", "idempotency", "log_config", "runtime_limit",
            "priority", "encryption", "audit", "deprecation_policy",
            "dependencies",
        ):
            if not hasattr(self, attr):
                object.__setattr__(self, attr, None)


def test_default_rules_include_secrets_rules():
    from pipecheck.rules import _DEFAULT_RULES
    rule_names = {type(r).__name__ for r in _DEFAULT_RULES}
    assert "NoSecretsConfigRule" in rule_names
    assert "InvalidSecretBackendRule" in rule_names
    assert "InsecureSecretBackendRule" in rule_names


def test_run_rules_includes_secrets_results():
    p = _MinimalPipeline(secrets={"backend": "vault"})
    results = run_rules(p)
    rule_names = {r.rule for r in results}
    assert "no-secrets-config" in rule_names
    assert "invalid-secret-backend" in rule_names
    assert "insecure-secret-backend" in rule_names


def test_pipeline_with_valid_secrets_passes_all_secrets_rules():
    p = _MinimalPipeline(secrets={"backend": "vault", "path": "secret/data/pipeline"})
    secrets_rules = [NoSecretsConfigRule(), InvalidSecretBackendRule(), InsecureSecretBackendRule()]
    results = run_rules(p, rules=secrets_rules)
    assert all(r.severity == Severity.OK for r in results)
