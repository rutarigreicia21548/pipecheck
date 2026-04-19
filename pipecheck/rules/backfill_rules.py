from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity


class NoBackfillConfigRule(Rule):
    id = "no-backfill-config"
    description = "Pipeline should define a backfill configuration."

    def check(self, pipeline) -> LintResult:
        val = getattr(pipeline, "backfill", None)
        if not val:
            return LintResult(
                rule_id=self.id,
                severity=Severity.WARNING,
                message="No backfill configuration defined.",
            )
        return LintResult(rule_id=self.id, severity=Severity.OK, message="OK")


class InvalidBackfillStrategyRule(Rule):
    id = "invalid-backfill-strategy"
    description = "Backfill strategy must be one of: full, incremental, none."

    VALID = {"full", "incremental", "none"}

    def check(self, pipeline) -> LintResult:
        backfill = getattr(pipeline, "backfill", None)
        if not isinstance(backfill, dict):
            return LintResult(rule_id=self.id, severity=Severity.OK, message="OK")
        strategy = backfill.get("strategy")
        if strategy is None:
            return LintResult(rule_id=self.id, severity=Severity.OK, message="OK")
        if strategy not in self.VALID:
            return LintResult(
                rule_id=self.id,
                severity=Severity.ERROR,
                message=f"Invalid backfill strategy '{strategy}'. Must be one of: {sorted(self.VALID)}.",
            )
        return LintResult(rule_id=self.id, severity=Severity.OK, message="OK")


class BackfillWindowTooLargeRule(Rule):
    id = "backfill-window-too-large"
    description = "Backfill window should not exceed 365 days."

    MAX_DAYS = 365

    def check(self, pipeline) -> LintResult:
        backfill = getattr(pipeline, "backfill", None)
        if not isinstance(backfill, dict):
            return LintResult(rule_id=self.id, severity=Severity.OK, message="OK")
        window = backfill.get("window_days")
        if window is None:
            return LintResult(rule_id=self.id, severity=Severity.OK, message="OK")
        if not isinstance(window, (int, float)) or window > self.MAX_DAYS:
            return LintResult(
                rule_id=self.id,
                severity=Severity.WARNING,
                message=f"Backfill window {window} days exceeds maximum of {self.MAX_DAYS} days.",
            )
        return LintResult(rule_id=self.id, severity=Severity.OK, message="OK")
