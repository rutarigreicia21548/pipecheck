import pytest
from dataclasses import dataclass, field
from pipecheck.rules.base import Severity
from pipecheck.rules.encryption_rules import (
    NoEncryptionRule,
    WeakEncryptionRule,
    UnrecognizedEncryptionRule,
)


@dataclass
class _FakePipeline:
    encryption: object = None


# --- NoEncryptionRule ---

def test_no_encryption_returns_warning():
    result = NoEncryptionRule().check(_FakePipeline())
    assert result.severity == Severity.WARNING


def test_empty_string_encryption_returns_warning():
    result = NoEncryptionRule().check(_FakePipeline(encryption=""))
    assert result.severity == Severity.WARNING


def test_encryption_present_passes_no_encryption_rule():
    result = NoEncryptionRule().check(_FakePipeline(encryption="AES-256"))
    assert result.severity == Severity.OK


# --- WeakEncryptionRule ---

def test_no_encryption_passes_weak_rule():
    result = WeakEncryptionRule().check(_FakePipeline())
    assert result.severity == Severity.OK


@pytest.mark.parametrize("weak", ["DES", "3DES", "RC4", "MD5", "SHA1"])
def test_weak_encryption_returns_error(weak):
    result = WeakEncryptionRule().check(_FakePipeline(encryption=weak))
    assert result.severity == Severity.ERROR
    assert weak in result.message


def test_lowercase_weak_encryption_returns_error():
    result = WeakEncryptionRule().check(_FakePipeline(encryption="des"))
    assert result.severity == Severity.ERROR


@pytest.mark.parametrize("strong", ["AES-256", "AES-128", "RSA-4096", "ChaCha20"])
def test_strong_encryption_passes_weak_rule(strong):
    result = WeakEncryptionRule().check(_FakePipeline(encryption=strong))
    assert result.severity == Severity.OK


# --- UnrecognizedEncryptionRule ---

def test_no_encryption_passes_unrecognized_rule():
    result = UnrecognizedEncryptionRule().check(_FakePipeline())
    assert result.severity == Severity.OK


@pytest.mark.parametrize("known", ["AES-256", "AES-128", "RSA-2048", "RSA-4096", "ChaCha20"])
def test_known_encryption_passes_unrecognized_rule(known):
    result = UnrecognizedEncryptionRule().check(_FakePipeline(encryption=known))
    assert result.severity == Severity.OK


def test_unknown_encryption_returns_warning():
    result = UnrecognizedEncryptionRule().check(_FakePipeline(encryption="BLOWFISH"))
    assert result.severity == Severity.WARNING
    assert "BLOWFISH" in result.message


def test_rule_names_are_set():
    assert NoEncryptionRule().name == "no-encryption"
    assert WeakEncryptionRule().name == "weak-encryption"
    assert UnrecognizedEncryptionRule().name == "unrecognized-encryption"
