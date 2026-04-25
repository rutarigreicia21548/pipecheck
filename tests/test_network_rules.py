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
class _FakePipeline:
    network: Any = None
    encryption: Any = None


# --- NoNetworkConfigRule ---

def test_no_network_returns_warning():
    result = NoNetworkConfigRule().check(_FakePipeline())
    assert result.severity == Severity.WARNING


def test_empty_dict_network_returns_warning():
    result = NoNetworkConfigRule().check(_FakePipeline(network={}))
    assert result.severity == Severity.WARNING


def test_network_present_passes_no_network_rule():
    result = NoNetworkConfigRule().check(_FakePipeline(network={"mode": "vpc"}))
    assert result.severity == Severity.OK


def test_network_string_passes_no_network_rule():
    result = NoNetworkConfigRule().check(_FakePipeline(network="vpc"))
    assert result.severity == Severity.OK


# --- InvalidNetworkModeRule ---

def test_no_network_passes_invalid_mode_rule():
    result = InvalidNetworkModeRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_non_dict_network_passes_invalid_mode_rule():
    result = InvalidNetworkModeRule().check(_FakePipeline(network="vpc"))
    assert result.severity == Severity.OK


def test_valid_network_modes_pass():
    for mode in ("vpc", "public", "private", "isolated", "peered"):
        result = InvalidNetworkModeRule().check(_FakePipeline(network={"mode": mode}))
        assert result.severity == Severity.OK, f"Expected OK for mode={mode}"


def test_invalid_network_mode_returns_error():
    result = InvalidNetworkModeRule().check(_FakePipeline(network={"mode": "open-internet"}))
    assert result.severity == Severity.ERROR
    assert "open-internet" in result.message


def test_no_mode_key_passes_invalid_mode_rule():
    result = InvalidNetworkModeRule().check(_FakePipeline(network={"ports": [8080]}))
    assert result.severity == Severity.OK


# --- TooManyOpenPortsRule ---

def test_no_network_passes_too_many_ports_rule():
    result = TooManyOpenPortsRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_ports_within_limit_passes():
    result = TooManyOpenPortsRule().check(_FakePipeline(network={"ports": list(range(5))}))
    assert result.severity == Severity.OK


def test_exactly_max_ports_passes():
    result = TooManyOpenPortsRule().check(_FakePipeline(network={"ports": list(range(10))}))
    assert result.severity == Severity.OK


def test_too_many_ports_returns_error():
    result = TooManyOpenPortsRule().check(_FakePipeline(network={"ports": list(range(11))}))
    assert result.severity == Severity.ERROR
    assert "11" in result.message


# --- PublicNetworkWithoutEncryptionRule ---

def test_no_network_passes_public_encryption_rule():
    result = PublicNetworkWithoutEncryptionRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_private_network_without_encryption_passes():
    result = PublicNetworkWithoutEncryptionRule().check(
        _FakePipeline(network={"mode": "private"})
    )
    assert result.severity == Severity.OK


def test_public_network_without_encryption_returns_error():
    result = PublicNetworkWithoutEncryptionRule().check(
        _FakePipeline(network={"mode": "public"})
    )
    assert result.severity == Severity.ERROR


def test_public_network_with_encryption_passes():
    result = PublicNetworkWithoutEncryptionRule().check(
        _FakePipeline(network={"mode": "public"}, encryption="AES-256")
    )
    assert result.severity == Severity.OK
