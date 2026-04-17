from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity


class NoCheckpointRule(Rule):
    id = "no_checkpoint"
    description = "Pipeline should define a checkpoint/restart strategy"

    def check(self, pipeline) -> LintResult:
        val = getattr(pipeline, "checkpoint", None)
        if not val:
            return LintResult(
                rule_id=self.id,
                severity=Severity.WARNING,
                message="No checkpoint strategy defined; long-running pipelines may not be resumable",
            )
        return LintResult(rule_id=self.id, severity=Severity.OK, message="Checkpoint strategy present")


class InvalidCheckpointIntervalRule(Rule):
    id = "invalid_checkpoint_interval"
    description = "Checkpoint interval must be a positive integer (seconds)"

    def check(self, pipeline) -> LintResult:
        interval = getattr(pipeline, "checkpoint_interval", None)
        if interval is None:
            return LintResult(rule_id=self.id, severity=Severity.OK, message="No checkpoint interval set")
        if not isinstance(interval, int) or interval <= 0:
            return LintResult(
                rule_id=self.id,
                severity=Severity.ERROR,
                message=f"Checkpoint interval must be a positive integer, got: {interval!r}",
            )
        return LintResult(rule_id=self.id, severity=Severity.OK, message="Checkpoint interval is valid")


class CheckpointIntervalTooLargeRule(Rule):
    id = "checkpoint_interval_too_large"
    description = "Checkpoint interval should not exceed 3600 seconds"
    MAX_INTERVAL = 3600

    def check(self, pipeline) -> LintResult:
        interval = getattr(pipeline, "checkpoint_interval", None)
        if interval is None:
            return LintResult(rule_id=self.id, severity=Severity.OK, message="No checkpoint interval set")
        if isinstance(interval, int) and interval > self.MAX_INTERVAL:
            return LintResult(
                rule_id=self.id,
                severity=Severity.WARNING,
                message=f"Checkpoint interval {interval}s exceeds recommended maximum of {self.MAX_INTERVAL}s",
            )
        return LintResult(rule_id=self.id, severity=Severity.OK, message="Checkpoint interval within bounds")
