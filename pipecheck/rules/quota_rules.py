from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pipecheck.rules.base import LintResult, Rule, Severity

_VALID_QUOTA_UNITS = {"requests/min", "requests/hour", "requests/day", "calls/min", "calls/hour"}
_MAX_QUOTA_LIMIT = 100_000


@dataclass
class NoQuotaConfigRule(Rule):
    name: str = "no-quota-config"
    description: str = "Pipeline should define a quota configuration."
    severity: Severity = Severity.WARNING

    def check(self, pipeline: Any) -> LintResult:
        quota = getattr(pipeline, "quota", None)
        if not quota:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                passed=False,
                message="No quota configuration found; consider defining quota limits.",
            )
        return LintResult(rule=self.name, severity=self.severity, passed=True, message="Quota configuration present.")


@dataclass
class InvalidQuotaUnitRule(Rule):
    name: str = "invalid-quota-unit"
    description: str = "Quota unit must be one of the recognised values."
    severity: Severity = Severity.ERROR

    def check(self, pipeline: Any) -> LintResult:
        quota = getattr(pipeline, "quota", None)
        if not isinstance(quota, dict):
            return LintResult(rule=self.name, severity=self.severity, passed=True, message="No quota dict to validate.")
        unit = quota.get("unit")
        if unit and unit not in _VALID_QUOTA_UNITS:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                passed=False,
                message=f"Invalid quota unit '{unit}'. Must be one of: {sorted(_VALID_QUOTA_UNITS)}.",
            )
        return LintResult(rule=self.name, severity=self.severity, passed=True, message="Quota unit is valid.")


@dataclass
class QuotaLimitTooHighRule(Rule):
    name: str = "quota-limit-too-high"
    description: str = f"Quota limit must not exceed {_MAX_QUOTA_LIMIT}."
    severity: Severity = Severity.WARNING

    def check(self, pipeline: Any) -> LintResult:
        quota = getattr(pipeline, "quota", None)
        if not isinstance(quota, dict):
            return LintResult(rule=self.name, severity=self.severity, passed=True, message="No quota dict to validate.")
        limit = quota.get("limit")
        if limit is not None and isinstance(limit, (int, float)) and limit > _MAX_QUOTA_LIMIT:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                passed=False,
                message=f"Quota limit {limit} exceeds maximum allowed value of {_MAX_QUOTA_LIMIT}.",
            )
        return LintResult(rule=self.name, severity=self.severity, passed=True, message="Quota limit is within bounds.")
