from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity


@dataclass
class NoConcurrencyLimitRule(Rule):
    name: str = "NoConcurrencyLimitRule"
    description: str = "Pipeline should define a concurrency limit"
    severity: Severity = Severity.WARNING

    def check(self, pipeline) -> LintResult:
        val = getattr(pipeline, "concurrency", None)
        if val is None:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message="No concurrency limit defined; unbounded parallelism may overload resources",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)


@dataclass
class ConcurrencyTooHighRule(Rule):
    name: str = "ConcurrencyTooHighRule"
    description: str = "Concurrency limit should not exceed recommended maximum"
    severity: Severity = Severity.WARNING
    max_concurrency: int = 32

    def check(self, pipeline) -> LintResult:
        val = getattr(pipeline, "concurrency", None)
        if val is not None and val > self.max_concurrency:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=f"Concurrency {val} exceeds recommended maximum of {self.max_concurrency}",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)


@dataclass
class ZeroConcurrencyRule(Rule):
    name: str = "ZeroConcurrencyRule"
    description: str = "Concurrency limit must be greater than zero"
    severity: Severity = Severity.ERROR

    def check(self, pipeline) -> LintResult:
        val = getattr(pipeline, "concurrency", None)
        if val is not None and val <= 0:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=f"Concurrency limit must be > 0, got {val}",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
