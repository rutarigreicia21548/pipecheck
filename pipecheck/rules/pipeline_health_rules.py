from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pipecheck.rules.base import LintResult, Rule, Severity

_HEALTHY_STATUSES = {"active", "healthy", "running"}
_DEGRADED_STATUSES = {"degraded", "unstable", "flapping"}
_TERMINAL_STATUSES = {"disabled", "archived", "deprecated", "failed"}


@dataclass
class NoPipelineHealthRule(Rule):
    name: str = "no-pipeline-health"
    description: str = "Pipeline should define a health status."
    severity: Severity = Severity.WARNING

    def check(self, pipeline: Any) -> LintResult:
        health = getattr(pipeline, "health", None)
        if not health:
            return LintResult(rule=self, passed=False, message="No health status defined for pipeline.")
        return LintResult(rule=self, passed=True)


@dataclass
class InvalidHealthStatusRule(Rule):
    name: str = "invalid-health-status"
    description: str = "Pipeline health status must be a recognised value."
    severity: Severity = Severity.ERROR

    def check(self, pipeline: Any) -> LintResult:
        health = getattr(pipeline, "health", None)
        if not health:
            return LintResult(rule=self, passed=True)
        all_known = _HEALTHY_STATUSES | _DEGRADED_STATUSES | _TERMINAL_STATUSES
        if isinstance(health, str) and health.lower() not in all_known:
            return LintResult(
                rule=self,
                passed=False,
                message=f"Unknown health status '{health}'. Expected one of: {sorted(all_known)}.",
            )
        return LintResult(rule=self, passed=True)


@dataclass
class TerminalHealthWithoutDeprecationRule(Rule):
    name: str = "terminal-health-without-deprecation"
    description: str = "Pipeline with a terminal health status should have a deprecation policy."
    severity: Severity = Severity.WARNING

    def check(self, pipeline: Any) -> LintResult:
        health = getattr(pipeline, "health", None)
        if not health or (isinstance(health, str) and health.lower() not in _TERMINAL_STATUSES):
            return LintResult(rule=self, passed=True)
        deprecation = getattr(pipeline, "deprecation_policy", None)
        if not deprecation:
            return LintResult(
                rule=self,
                passed=False,
                message=(
                    f"Pipeline has terminal health status '{health}' but no deprecation_policy is set."
                ),
            )
        return LintResult(rule=self, passed=True)
