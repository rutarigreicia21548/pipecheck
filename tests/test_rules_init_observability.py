import pytest
from dataclasses import dataclass, field
from typing import Any
from pipecheck.rules import run_rules
from pipecheck.rules.observability_rules import (
    NoObservabilityConfigRule,
    InvalidTracingBackendRule,
    InvalidMetricsBackendRule,
    TooManyCustomMetricsRule,
)


@dataclass
class _MinimalPipeline:
    pipeline_id: str = "obs_test_pipeline"
    schedule: str = "@daily"
    tags: list = field(default_factory=lambda: ["team:data"])
    owner: str = "data-team"
    retries: int = 1
    observability: Any = None

    def __post_init__(self):
        # Satisfy any attribute lookups from other rules
        for attr in [
            "description", "environment", "timeout", "concurrency",
            "alerts", "sla", "labels", "memory_limit", "cpu_limit",
            "notifications", "version", "metadata", "access_level",
            "allowed_roles", "data_quality_checks", "checkpoint",
            "lineage", "trigger", "cost_estimate", "cost_tier",
            "compliance_tag", "cache_strategy", "parallelism",
            "backfill", "idempotency", "log_config", "runtime_limit",
            "priority", "encryption", "audit", "deprecation_policy",
            "secrets", "rollback",
        ]:
            if not hasattr(self, attr):
                object.__setattr__(self, attr, None)


def test_default_rules_include_observability_rules():
    pipeline = _MinimalPipeline()
    results = run_rules(pipeline)
    rule_names = {r.rule for r in results}
    assert "no_observability_config" in rule_names


def test_run_rules_includes_observability_results():
    pipeline = _MinimalPipeline(
        observability={
            "tracing_backend": "opentelemetry",
            "metrics_backend": "prometheus",
        }
    )
    results = run_rules(pipeline)
    obs_results = [r for r in results if "observability" in r.rule or "tracing" in r.rule or "metrics" in r.rule]
    assert len(obs_results) >= 1


def test_pipeline_with_valid_observability_passes_all_obs_rules():
    pipeline = _MinimalPipeline(
        observability={
            "tracing_backend": "datadog",
            "metrics_backend": "datadog",
            "custom_metrics": ["job_duration"],
        }
    )
    rules = [
        NoObservabilityConfigRule(),
        InvalidTracingBackendRule(),
        InvalidMetricsBackendRule(),
        TooManyCustomMetricsRule(),
    ]
    results = [r.check(pipeline) for r in rules]
    assert all(r.passed for r in results), [r.message for r in results if not r.passed]
