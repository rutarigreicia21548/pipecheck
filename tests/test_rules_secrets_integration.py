from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pipecheck.rules.base import Severity
from pipecheck.rules.secrets_rules import (
    InsecureSecretBackendRule,
    InvalidSecretBackendRule,
    NoSecretsConfigRule,
)

_SECRETS_RULES = [NoSecretsConfigRule(), InvalidSecretBackendRule(), InsecureSecretBackendRule()]


@dataclass
class _FullPipeline:
    secrets: Any = None


def _run(pipeline):
    return [rule.check(pipeline) for rule in _SECRETS_RULES]


def test_valid_vault_secrets_all_pass():
    p = _FullPipeline(secrets={"backend": "vault", "path": "secret/data/myapp"})
    results = _run(p)
    assert all(r.severity == Severity.OK for r in results)


def test_missing_secrets_produces_warning():
    p = _FullPipeline(secrets=None)
    results = _run(p)
    severities = {r.rule: r.severity for r in results}
    assert severities["no-secrets-config"] == Severity.WARNING
    # other rules should be OK when no secrets dict present
    assert severities["invalid-secret-backend"] == Severity.OK
    assert severities["insecure-secret-backend"] == Severity.OK


def test_insecure_backend_produces_warning():
    p = _FullPipeline(secrets={"backend": "env"})
    results = _run(p)
    severities = {r.rule: r.severity for r in results}
    assert severities["no-secrets-config"] == Severity.OK
    assert severities["insecure-secret-backend"] == Severity.WARNING


def test_invalid_backend_produces_error():
    p = _FullPipeline(secrets={"backend": "hardcoded"})
    results = _run(p)
    severities = {r.rule: r.severity for r in results}
    assert severities["invalid-secret-backend"] == Severity.ERROR
