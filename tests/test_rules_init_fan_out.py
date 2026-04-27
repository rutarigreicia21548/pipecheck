from dataclasses import dataclass, field
from typing import Any, Optional

from pipecheck.rules import run_rules
from pipecheck.rules.fan_out_rules import (
    FanInTooHighRule,
    FanOutTooHighRule,
    InvalidFanOutStrategyRule,
    NoFanOutConfigRule,
)


@dataclass
class _MinimalPipeline:
    pipeline_id: str = "test_pipeline"
    name: str = "Test Pipeline"
    schedule: str = "@daily"
    tags: tuple = ("team:data",)
    owner: str = "data-team"
    description: str = "A test pipeline."
    environment: str = "production"
    retries: int = 2
    retry_delay: int = 300
    timeout: int = 3600
    concurrency: int = 4
    alerts: tuple = ("slack:#alerts",)
    sla: int = 7200
    labels: tuple = ("env:production",)
    memory_limit: int = 2048
    cpu_limit: float = 1.0
    notifications: tuple = field(default_factory=lambda: ({"type": "email", "event": "failure"},))
    version: str = "1.0.0"
    metadata: dict = field(default_factory=lambda: {"team": "data"})
    access_level: str = "internal"
    allowed_roles: tuple = ("analyst",)
    data_quality_checks: tuple = ("not_null",)
    checkpoint: str = "enabled"
    checkpoint_interval: int = 100
    lineage: dict = field(default_factory=lambda: {"inputs": ["src"], "outputs": ["dst"]})
    trigger: dict = field(default_factory=lambda: {"type": "schedule"})
    cost_estimate: float = 1.5
    cost_tier: str = "low"
    compliance_tag: str = "public"
    cache_strategy: str = "lru"
    cache_ttl: int = 3600
    parallelism: int = 4
    backfill: dict = field(default_factory=lambda: {"strategy": "full"})
    idempotency: dict = field(default_factory=lambda: {"strategy": "upsert", "key": "id"})
    log_config: dict = field(default_factory=lambda: {"level": "INFO", "retention_days": 30})
    runtime_limit: int = 3600
    priority: str = "normal"
    encryption: str = "AES-256"
    audit: dict = field(default_factory=lambda: {"level": "full", "retention_days": 90})
    deprecation_policy: dict = field(default_factory=lambda: {"date": "2099-01-01", "active": True})
    secrets: dict = field(default_factory=lambda: {"backend": "vault"})
    rollback: dict = field(default_factory=lambda: {"strategy": "revert"})
    observability: dict = field(default_factory=lambda: {"tracing": "jaeger", "metrics": "prometheus"})
    runbook: str = "https://wiki.example.com/runbook"
    changelog: str = "https://wiki.example.com/changelog"
    freshness: dict = field(default_factory=lambda: {"unit": "hours", "value": 6})
    rate_limit: dict = field(default_factory=lambda: {"unit": "minute", "limit": 100})
    security: dict = field(default_factory=lambda: {"scan_level": "full", "auth_method": "oauth2"})
    storage: dict = field(default_factory=lambda: {"backend": "s3", "storage_class": "standard"})
    health_status: str = "healthy"
    network: dict = field(default_factory=lambda: {"mode": "vpc", "open_ports": [443]})
    windowing: dict = field(default_factory=lambda: {"type": "tumbling", "size": 3600})
    profiling: dict = field(default_factory=lambda: {"backend": "pyroscope", "sample_rate": 0.05})
    quota: dict = field(default_factory=lambda: {"unit": "requests", "limit": 1000})
    drift: dict = field(default_factory=lambda: {"strategy": "statistical", "threshold": 0.05})
    fan_out: dict = field(default_factory=lambda: {"strategy": "scatter", "degree": 3, "fan_in": 3})


def test_default_rules_include_fan_out_rules():
    from pipecheck.rules import _DEFAULT_RULES  # type: ignore
    rule_types = [type(r) for r in _DEFAULT_RULES]
    assert NoFanOutConfigRule in rule_types
    assert FanOutTooHighRule in rule_types
    assert FanInTooHighRule in rule_types
    assert InvalidFanOutStrategyRule in rule_types


def test_run_rules_includes_fan_out_results():
    pipeline = _MinimalPipeline()
    results = run_rules(pipeline)
    rule_names = {r.rule for r in results}
    assert "no-fan-out-config" in rule_names
    assert "fan-out-too-high" in rule_names


def test_pipeline_with_valid_fan_out_passes_all_fan_out_rules():
    pipeline = _MinimalPipeline()
    results = run_rules(pipeline)
    fan_out_results = [
        r for r in results
        if r.rule in {"no-fan-out-config", "fan-out-too-high", "fan-in-too-high", "invalid-fan-out-strategy"}
    ]
    failures = [r for r in fan_out_results if not r.passed]
    assert not failures, [r.message for r in failures]
