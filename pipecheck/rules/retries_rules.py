from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity


@dataclass
class NoRetriesRule(Rule):
    name: str = "no-retries"
    description: str = "Pipeline should define a retry count"
    severity: Severity = Severity.WARNING

    def check(self, pipeline) -> LintResult:
        retries = getattr(pipeline, "retries", None)
        if retries is None:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=f"Pipeline '{pipeline.id or pipeline.name}' does not define retries.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="", passed=True)


@dataclass
class TooManyRetriesRule(Rule):
    name: str = "too-many-retries"
    description: str = "Pipeline retry count should not exceed a reasonable limit"
    severity: Severity = Severity.WARNING
    max_retries: int = 5

    def check(self, pipeline) -> LintResult:
        retries = getattr(pipeline, "retries", None)
        if retries is not None and retries > self.max_retries:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=(
                    f"Pipeline '{pipeline.id or pipeline.name}' has {retries} retries, "
                    f"which exceeds the recommended maximum of {self.max_retries}."
                ),
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="", passed=True)


@dataclass
class NoRetryDelayRule(Rule):
    name: str = "no-retry-delay"
    description: str = "Pipeline with retries should define a retry delay"
    severity: Severity = Severity.INFO

    def check(self, pipeline) -> LintResult:
        retries = getattr(pipeline, "retries", None)
        retry_delay = getattr(pipeline, "retry_delay", None)
        if retries and retries > 0 and retry_delay is None:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=(
                    f"Pipeline '{pipeline.id or pipeline.name}' defines retries but no retry_delay."
                ),
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="", passed=True)
