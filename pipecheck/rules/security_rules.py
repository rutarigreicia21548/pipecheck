from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pipecheck.rules.base import LintResult, Rule, Severity

VALID_SCAN_LEVELS = {"basic", "standard", "strict"}
INSECURE_SCAN_LEVELS = {"none", "disabled", "off"}
VALID_AUTH_METHODS = {"iam", "oauth2", "api_key", "service_account", "mtls"}
WEAK_AUTH_METHODS = {"basic", "none", "anonymous"}


@dataclass
class NoSecurityConfigRule(Rule):
    name: str = "no_security_config"
    description: str = "Pipeline should define a security configuration."
    severity: Severity = Severity.WARNING

    def check(self, pipeline: Any) -> LintResult:
        security = getattr(pipeline, "security", None)
        if not security:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message="No security configuration defined.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, passed=True)


@dataclass
class InvalidScanLevelRule(Rule):
    name: str = "invalid_scan_level"
    description: str = "Security scan level must be a recognised value."
    severity: Severity = Severity.ERROR

    def check(self, pipeline: Any) -> LintResult:
        security = getattr(pipeline, "security", None)
        if not isinstance(security, dict):
            return LintResult(rule=self.name, severity=self.severity, passed=True)
        scan_level = security.get("scan_level")
        if scan_level is None:
            return LintResult(rule=self.name, severity=self.severity, passed=True)
        if str(scan_level).lower() in INSECURE_SCAN_LEVELS:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=f"Scan level '{scan_level}' disables security scanning.",
                passed=False,
            )
        if str(scan_level).lower() not in VALID_SCAN_LEVELS:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=(
                    f"Scan level '{scan_level}' is not valid. "
                    f"Expected one of: {sorted(VALID_SCAN_LEVELS)}."
                ),
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, passed=True)


@dataclass
class WeakAuthMethodRule(Rule):
    name: str = "weak_auth_method"
    description: str = "Pipeline auth method should not be weak or anonymous."
    severity: Severity = Severity.ERROR

    def check(self, pipeline: Any) -> LintResult:
        security = getattr(pipeline, "security", None)
        if not isinstance(security, dict):
            return LintResult(rule=self.name, severity=self.severity, passed=True)
        auth_method = security.get("auth_method")
        if auth_method is None:
            return LintResult(rule=self.name, severity=self.severity, passed=True)
        if str(auth_method).lower() in WEAK_AUTH_METHODS:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=(
                    f"Auth method '{auth_method}' is considered weak. "
                    f"Use one of: {sorted(VALID_AUTH_METHODS)}."
                ),
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, passed=True)
