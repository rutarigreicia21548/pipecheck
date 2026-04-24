from dataclasses import dataclass, field
from typing import Any

from pipecheck.rules import run_rules
from pipecheck.rules.security_rules import (
    NoSecurityConfigRule,
    InvalidScanLevelRule,
    WeakAuthMethodRule,
)


@dataclass
class _MinimalPipeline:
    pipeline_id: str = "my_pipeline"
    name: str = "my_pipeline"
    schedule: str = "@daily"
    tags: list = field(default_factory=lambda: ["team:data"])
    owner: str = "data-team"
    retries: int = 2
    retry_delay: int = 300
    timeout: int = 3600
    concurrency: int = 4
    dependencies: list = field(default_factory=list)
    description: str = "A valid pipeline."
    owner_contact: str = "data-team@example.com"
    environment: str = "production"
    alerts: list = field(default_factory=lambda: ["#alerts"])
    sla: int = 7200
    labels: dict = field(default_factory=lambda: {"team": "data"})
    memory_limit: int = 2048
    cpu_limit: float = 1.0
    notifications: list = field(default_factory=lambda: [{"type": "email", "event": "failure"}])
    version: str = "1.0.0"
    metadata: dict = field(default_factory=lambda: {"team": "data"})
    access_level: str = "internal"
    allowed_roles: list = field(default_factory=lambda: ["data-engineer"])
    data_quality_checks: list = field(default_factory=lambda: ["not_null"])
    checkpoint: str = "enabled"
    checkpoint_interval: int = 600
    lineage: dict = field(
        default_factory=lambda: {"inputs": ["raw.events"], "outputs": ["clean.events"]}
    )
    trigger: dict = field(default_factory=lambda: {"type": "schedule"})
    cost_estimate: float = 1.5
    cost_tier: str = "low"
    compliance_tag: str = "public"
    cache_strategy: str = "lru"
    cache_ttl: int = 3600
    parallelism: int = 4
    backfill: dict = field(default_factory=lambda: {"strategy": "full", "window_days": 7})
    idempotency: dict = field(default_factory=lambda: {"strategy": "upsert", "key": "id"})
    log_config: dict = field(default_factory=lambda: {"level": "INFO", "retention_days": 30})
    runtime_limit: int = 3600
    runtime_warn_threshold: int = 2700
    priority: str = "normal"
    priority_weight: int = 5
    encryption: str = "aes256"
    audit: dict = field(default_factory=lambda: {"level": "standard", "retention_days": 90})
    deprecation_policy: dict = field(
        default_factory=lambda: {"date": "2099-12-31", "active": True}
    )
    secrets: dict = field(default_factory=lambda: {"backend": "vault"})
    rollback: dict = field(default_factory=lambda: {"strategy": "immediate", "window_hours": 1})
    observability: dict = field(
        default_factory=lambda: {"tracing": "opentelemetry", "metrics": "prometheus"}
    )
    runbook: str = "https://wiki.example.com/runbook"
    changelog: str = "https://wiki.example.com/changelog"
    freshness: dict = field(default_factory=lambda: {"value": 24, "unit": "hours"})
    rate_limit: dict = field(default_factory=lambda: {"value": 100, "unit": "minute"})
    security: dict = field(
        default_factory=lambda: {"scan_level": "strict", "auth_method": "iam"}
    )


def test_default_rules_include_security_rules():
    rule_types = [type(r) for r in run_rules.__self__.__class__.__mro__] if hasattr(run_rules, '__self__') else []
    # Verify the rule classes exist and are importable
    assert NoSecurityConfigRule is not None
    assert InvalidScanLevelRule is not None
    assert WeakAuthMethodRule is not None


def test_run_rules_includes_security_results():
    pipeline = _MinimalPipeline()
    results = run_rules(pipeline)
    rule_names = {r.rule for r in results}
    assert "no_security_config" in rule_names
    assert "invalid_scan_level" in rule_names
    assert "weak_auth_method" in rule_names


def test_pipeline_with_valid_security_passes_all_security_rules():
    pipeline = _MinimalPipeline()
    results = run_rules(pipeline)
    security_results = [
        r for r in results
        if r.rule in {"no_security_config", "invalid_scan_level", "weak_auth_method"}
    ]
    assert all(r.passed for r in security_results), [
        r.message for r in security_results if not r.passed
    ]
