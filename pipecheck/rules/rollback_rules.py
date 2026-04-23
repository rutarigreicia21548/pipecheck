from __future__ import annotations

from pipecheck.rules.base import LintResult, Rule, Severity

VALID_ROLLBACK_STRATEGIES = {"full", "partial", "checkpoint", "none"}
MAX_ROLLBACK_WINDOW_DAYS = 30


class NoRollbackConfigRule(Rule):
    name = "no-rollback-config"
    description = "Pipeline should define a rollback configuration."
    severity = Severity.WARNING

    def check(self, pipeline) -> LintResult:
        rb = getattr(pipeline, "rollback", None)
        if not rb:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message="No rollback configuration defined.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, passed=True)


class InvalidRollbackStrategyRule(Rule):
    name = "invalid-rollback-strategy"
    description = "Rollback strategy must be one of the recognised values."
    severity = Severity.ERROR

    def check(self, pipeline) -> LintResult:
        rb = getattr(pipeline, "rollback", None)
        if not isinstance(rb, dict):
            return LintResult(rule=self.name, severity=self.severity, passed=True)
        strategy = rb.get("strategy")
        if strategy is None:
            return LintResult(rule=self.name, severity=self.severity, passed=True)
        if strategy not in VALID_ROLLBACK_STRATEGIES:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=(
                    f"Invalid rollback strategy '{strategy}'. "
                    f"Expected one of: {sorted(VALID_ROLLBACK_STRATEGIES)}."
                ),
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, passed=True)


class RollbackWindowTooLargeRule(Rule):
    name = "rollback-window-too-large"
    description = f"Rollback window must not exceed {MAX_ROLLBACK_WINDOW_DAYS} days."
    severity = Severity.WARNING

    def check(self, pipeline) -> LintResult:
        rb = getattr(pipeline, "rollback", None)
        if not isinstance(rb, dict):
            return LintResult(rule=self.name, severity=self.severity, passed=True)
        window = rb.get("window_days")
        if window is None:
            return LintResult(rule=self.name, severity=self.severity, passed=True)
        if window > MAX_ROLLBACK_WINDOW_DAYS:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=(
                    f"Rollback window {window} days exceeds maximum "
                    f"of {MAX_ROLLBACK_WINDOW_DAYS} days."
                ),
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, passed=True)


ROLLBACK_RULES: list[Rule] = [
    NoRollbackConfigRule(),
    InvalidRollbackStrategyRule(),
    RollbackWindowTooLargeRule(),
]
