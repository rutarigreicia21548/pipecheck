from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from pipecheck.rules.base import Severity
from pipecheck.rules.secrets_rules import (
    InsecureSecretBackendRule,
    InvalidSecretBackendRule,
    NoSecretsConfigRule,
)


@dataclass
class _FakePipeline:
    secrets: Any = None


# --- NoSecretsConfigRule ---

def test_no_secrets_returns_warning():
    result = NoSecretsConfigRule().check(_FakePipeline())
    assert result.severity == Severity.WARNING


def test_empty_dict_secrets_returns_warning():
    result = NoSecretsConfigRule().check(_FakePipeline(secrets={}))
    assert result.severity == Severity.WARNING


def test_secrets_present_passes_no_secrets_rule():
    result = NoSecretsConfigRule().check(_FakePipeline(secrets={"backend": "vault"}))
    assert result.severity == Severity.OK


def test_secrets_string_passes_no_secrets_rule():
    result = NoSecretsConfigRule().check(_FakePipeline(secrets="vault"))
    assert result.severity == Severity.OK


# --- InvalidSecretBackendRule ---

def test_no_secrets_passes_invalid_backend_rule():
    result = InvalidSecretBackendRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_valid_backends_pass():
    for backend in ("vault", "aws_secrets_manager", "gcp_secret_manager", "azure_key_vault", "env"):
        result = InvalidSecretBackendRule().check(_FakePipeline(secrets={"backend": backend}))
        assert result.severity == Severity.OK, f"{backend} should be valid"


def test_invalid_backend_returns_error():
    result = InvalidSecretBackendRule().check(_FakePipeline(secrets={"backend": "my_custom_db"}))
    assert result.severity == Severity.ERROR
    assert "my_custom_db" in result.message


def test_no_backend_key_passes_invalid_rule():
    result = InvalidSecretBackendRule().check(_FakePipeline(secrets={"path": "/secret/myapp"}))
    assert result.severity == Severity.OK


# --- InsecureSecretBackendRule ---

def test_no_secrets_passes_insecure_rule():
    result = InsecureSecretBackendRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_env_backend_returns_warning():
    result = InsecureSecretBackendRule().check(_FakePipeline(secrets={"backend": "env"}))
    assert result.severity == Severity.WARNING
    assert "env" in result.message


def test_plaintext_backend_returns_warning():
    result = InsecureSecretBackendRule().check(_FakePipeline(secrets={"backend": "plaintext"}))
    assert result.severity == Severity.WARNING


def test_vault_backend_passes_insecure_rule():
    result = InsecureSecretBackendRule().check(_FakePipeline(secrets={"backend": "vault"}))
    assert result.severity == Severity.OK


def test_aws_backend_passes_insecure_rule():
    result = InsecureSecretBackendRule().check(_FakePipeline(secrets={"backend": "aws_secrets_manager"}))
    assert result.severity == Severity.OK
