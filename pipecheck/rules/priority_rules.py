from __future__ import annotations
from dataclasses import dataclass
from pipecheck.rules.base import LintResult, Rule, Severity

VALID_PRIORITIES = {"critical", "high", "medium", "low"}
MAX_PRIORITY_WEIGHT = 100


@dataclass
class NoPriorityRule(Rule):
    name: str = "no-priority"
    description: str = "Pipeline should define a priority level."
    severity: Severity = Severity.WARNING

    def check(self, pipeline) -> LintResult:
        priority = getattr(pipeline, "priority", None)
        if not priority:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message="No priority defined. Consider setting a priority level (critical, high, medium, low).",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="Priority is set.", passed=True)


@dataclass
class InvalidPriorityLevelRule(Rule):
    name: str = "invalid-priority-level"
    description: str = "Priority must be one of: critical, high, medium, low."
    severity: Severity = Severity.ERROR

    def check(self, pipeline) -> LintResult:
        priority = getattr(pipeline, "priority", None)
        if not priority:
            return LintResult(rule=self.name, severity=self.severity, message="No priority to validate.", passed=True)
        if isinstance(priority, str) and priority.lower() not in VALID_PRIORITIES:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=f"Invalid priority '{priority}'. Must be one of: {sorted(VALID_PRIORITIES)}.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="Priority level is valid.", passed=True)


@dataclass
class PriorityWeightTooHighRule(Rule):
    name: str = "priority-weight-too-high"
    description: str = f"Priority weight must not exceed {MAX_PRIORITY_WEIGHT}."
    severity: Severity = Severity.ERROR

    def check(self, pipeline) -> LintResult:
        weight = getattr(pipeline, "priority_weight", None)
        if weight is None:
            return LintResult(rule=self.name, severity=self.severity, message="No priority weight to validate.", passed=True)
        if isinstance(weight, (int, float)) and weight > MAX_PRIORITY_WEIGHT:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=f"Priority weight {weight} exceeds maximum of {MAX_PRIORITY_WEIGHT}.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="Priority weight is within bounds.", passed=True)
