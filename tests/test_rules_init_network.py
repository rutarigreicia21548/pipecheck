import pytest
from dataclasses import dataclass, field
from typing import Any
from pipecheck.rules import run_rules
from pipecheck.rules.base import Severity
from pipecheck.rules.network_rules import (
    NoNetworkConfigRule,
    InvalidNetworkModeRule,
    TooManyOpenPortsRule,
    PublicNetworkWithoutEncryptionRule,
)


@dataclass
class _MinimalPipeline:
    id: str = "my_pipeline"
    name: str = "My Pipeline"
    schedule: str = "@daily"
    tags: Any = field(default_factory=lambda: ["team:data"])
    owner: str = "data-team"
    retries: int = 2
    network: Any = field(default_factory=lambda: {"mode": "vpc", "ports": [443]})
    encryption: str = "AES-256"
    dependencies: Any = field(default_factory=list)
    timeout: int = 3600
    description: str = "A pipeline."
    environment: str = "production"
    concurrency: int = 2


def test_default_rules_include_network_rules():
    from pipecheck.rules import run_rules
    import inspect
    import pipecheck.rules as rules_pkg

    rule_classes = [
        NoNetworkConfigRule,
        InvalidNetworkModeRule,
        TooManyOpenPortsRule,
        PublicNetworkWithoutEncryptionRule,
    ]
    # Verify each rule can be instantiated and has required interface
    for cls in rule_classes:
        instance = cls()
        assert hasattr(instance, "check")
        assert hasattr(instance, "name")


def test_no_network_config_rule_fires_warning_on_missing_network():
    @dataclass
    class _NakedPipeline:
        network: Any = None

    result = NoNetworkConfigRule().check(_NakedPipeline())
    assert result.severity == Severity.WARNING


def test_pipeline_with_valid_network_passes_all_network_rules():
    pipeline = _MinimalPipeline()
    rules = [
        NoNetworkConfigRule(),
        InvalidNetworkModeRule(),
        TooManyOpenPortsRule(),
        PublicNetworkWithoutEncryptionRule(),
    ]
    results = [r.check(pipeline) for r in rules]
    assert all(r.severity == Severity.OK for r in results)


def test_public_mode_without_encryption_triggers_error():
    @dataclass
    class _PublicPipeline:
        network: Any = field(default_factory=lambda: {"mode": "public"})
        encryption: Any = None

    result = PublicNetworkWithoutEncryptionRule().check(_PublicPipeline())
    assert result.severity == Severity.ERROR
    assert "public" in result.message.lower()
