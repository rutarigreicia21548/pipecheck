from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pipecheck.rules.base import LintResult, Rule, Severity

_VALID_DRIFT_STRATEGIES = {"alert", "auto-correct", "ignore", "fail"}
_MAX_DRIFT_THRESHOLD = 100


@dataclass
class NoDriftConfigRule(Rule):
    name: str = "no-drift-config"
    description: str = "Pipeline should define a drift detection configuration."
    severity: Severity = Severity.WARNING

    def check(self, pipeline: Any) -> LintResult:
        drift = getattr(pipeline, "drift", None)
        if not drift:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message="No drift detection configuration defined.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, passed=True)


@dataclass
class InvalidDriftStrategyRule(Rule):
    name: str = "invalid-drift-strategy"
    description: str = "Drift detection strategy must be a recognised value."
    severity: Severity = Severity.ERROR

    def check(self, pipeline: Any) -> LintResult:
        drift = getattr(pipeline, "drift", None)
        if not isinstance(drift, dict):
            return LintResult(rule=self.name, severity=self.severity, passed=True)
        strategy = drift.get("strategy")
        if strategy is not None and strategy not in _VALID_DRIFT_STRATEGIES:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=(
                    f"Invalid drift strategy '{strategy}'. "
                    f"Must be one of: {sorted(_VALID_DRIFT_STRATEGIES)}."
                ),
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, passed=True)


@dataclass
class DriftThresholdTooHighRule(Rule):
    name: str = "drift-threshold-too-high"
    description: str = f"Drift threshold must not exceed {_MAX_DRIFT_THRESHOLD}%."
    severity: Severity = Severity.WARNING

    def check(self, pipeline: Any) -> LintResult:
        drift = getattr(pipeline, "drift", None)
        if not isinstance(drift, dict):
            return LintResult(rule=self.name, severity=self.severity, passed=True)
        threshold = drift.get("threshold")
        if threshold is not None and threshold > _MAX_DRIFT_THRESHOLD:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=(
                    f"Drift threshold {threshold}% exceeds maximum "
                    f"allowed {_MAX_DRIFT_THRESHOLD}%."
                ),
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, passed=True)
