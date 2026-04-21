from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pipecheck.rules.base import LintResult, Rule, Severity

_VALID_SECRET_BACKENDS = {"vault", "aws_secrets_manager", "gcp_secret_manager", "azure_key_vault", "env"}
_INSECURE_BACKENDS = {"env", "plaintext"}


@dataclass
class NoSecretsConfigRule(Rule):
    name: str = "no-secrets-config"
    description: str = "Pipeline should define a secrets configuration."

    def check(self, pipeline: Any) -> LintResult:
        secrets = getattr(pipeline, "secrets", None)
        if not secrets:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="No secrets configuration defined; consider specifying a secrets backend.",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Secrets configuration present.")


@dataclass
class InvalidSecretBackendRule(Rule):
    name: str = "invalid-secret-backend"
    description: str = "Secrets backend must be a recognised provider."

    def check(self, pipeline: Any) -> LintResult:
        secrets = getattr(pipeline, "secrets", None)
        if not isinstance(secrets, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="No backend to validate.")
        backend = secrets.get("backend")
        if backend and backend not in _VALID_SECRET_BACKENDS:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Unknown secrets backend '{backend}'. Valid options: {sorted(_VALID_SECRET_BACKENDS)}.",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Secrets backend is valid.")


@dataclass
class InsecureSecretBackendRule(Rule):
    name: str = "insecure-secret-backend"
    description: str = "Warn when an insecure secrets backend such as 'env' or 'plaintext' is used."

    def check(self, pipeline: Any) -> LintResult:
        secrets = getattr(pipeline, "secrets", None)
        if not isinstance(secrets, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="No backend to evaluate.")
        backend = secrets.get("backend", "")
        if backend in _INSECURE_BACKENDS:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message=f"Secrets backend '{backend}' is considered insecure for production use.",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Secrets backend is secure.")
