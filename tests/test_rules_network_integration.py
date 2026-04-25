import pytest
from dataclasses import dataclass, field
from typing import Any
from pipecheck.rules.base import Severity
from pipecheck.rules.network_rules import (
    NoNetworkConfigRule,
    InvalidNetworkModeRule,
    TooManyOpenPortsRule,
    PublicNetworkWithoutEncryptionRule,
)


@dataclass
class _FullPipeline:
    network: Any = None
    encryption: Any = None


def _network_rules():
    return [
        NoNetworkConfigRule(),
        InvalidNetworkModeRule(),
        TooManyOpenPortsRule(),
        PublicNetworkWithoutEncryptionRule(),
    ]


def _check_all(pipeline):
    return [rule.check(pipeline) for rule in _network_rules()]


def test_valid_vpc_network_all_pass():
    pipeline = _FullPipeline(
        network={"mode": "vpc", "ports": [443, 8080]},
        encryption="AES-256",
    )
    results = _check_all(pipeline)
    assert all(r.severity == Severity.OK for r in results)


def test_missing_network_produces_warning():
    pipeline = _FullPipeline()
    results = _check_all(pipeline)
    warnings = [r for r in results if r.severity == Severity.WARNING]
    assert any(r.rule == "no-network-config" for r in warnings)


def test_invalid_mode_produces_error():
    pipeline = _FullPipeline(network={"mode": "flat"})
    results = _check_all(pipeline)
    errors = [r for r in results if r.severity == Severity.ERROR]
    assert any(r.rule == "invalid-network-mode" for r in errors)


def test_public_without_encryption_produces_error():
    pipeline = _FullPipeline(network={"mode": "public"})
    results = _check_all(pipeline)
    errors = [r for r in results if r.severity == Severity.ERROR]
    assert any(r.rule == "public-network-without-encryption" for r in errors)


def test_too_many_ports_produces_error():
    pipeline = _FullPipeline(
        network={"mode": "private", "ports": list(range(15))}
    )
    results = _check_all(pipeline)
    errors = [r for r in results if r.severity == Severity.ERROR]
    assert any(r.rule == "too-many-open-ports" for r in errors)
