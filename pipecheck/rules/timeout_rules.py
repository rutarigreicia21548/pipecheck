from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity


@dataclass
class NoTimeoutRule(Rule):
    name: str = "no-timeout"
    description: str = "Pipeline should define an execution timeout"
    severity: Severity = Severity.WARNING

    def check(self, pipeline) -> LintResult:
        timeout = getattr(pipeline, "timeout", None)
        if timeout is None:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=f"Pipeline '{pipeline.id or pipeline.name}' has no timeout defined.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)


@dataclass
class TimeoutTooLongRule(Rule):
    name: str = "timeout-too-long"
    description: str = "Pipeline timeout should not exceed a reasonable maximum"
    severity: Severity = Severity.WARNING
    max_seconds: int = 3600  # 1 hour

    def check(self, pipeline) -> LintResult:
        timeout = getattr(pipeline, "timeout", None)
        if timeout is None:
            return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
        try:
            seconds = int(timeout)
        except (TypeError, ValueError):
            return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
        if seconds > self.max_seconds:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=(
                    f"Pipeline '{pipeline.id or pipeline.name}' timeout {seconds}s "
                    f"exceeds maximum allowed {self.max_seconds}s."
                ),
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)


@dataclass
class ZeroTimeoutRule(Rule):
    name: str = "zero-timeout"
    description: str = "Pipeline timeout must be greater than zero"
    severity: Severity = Severity.ERROR

    def check(self, pipeline) -> LintResult:
        timeout = getattr(pipeline, "timeout", None)
        if timeout is None:
            return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
        try:
            seconds = int(timeout)
        except (TypeError, ValueError):
            return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
        if seconds <= 0:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=(
                    f"Pipeline '{pipeline.id or pipeline.name}' has a non-positive timeout ({seconds}s)."
                ),
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
