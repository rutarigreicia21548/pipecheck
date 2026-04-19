from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity

MAX_PARALLELISM = 32


@dataclass
class NoParallelismRule(Rule):
    name: str = "no_parallelism"
    description: str = "Pipeline should define a parallelism limit"

    def check(self, pipeline) -> LintResult:
        val = getattr(pipeline, "parallelism", None)
        if val is None:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="No parallelism limit defined; unbounded concurrency may overload workers",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Parallelism limit present")


@dataclass
class ParallelismTooHighRule(Rule):
    name: str = "parallelism_too_high"
    description: str = f"Parallelism limit should not exceed {MAX_PARALLELISM}"

    def check(self, pipeline) -> LintResult:
        val = getattr(pipeline, "parallelism", None)
        if val is None:
            return LintResult(rule=self.name, severity=Severity.OK, message="No parallelism set; skipping")
        if val > MAX_PARALLELISM:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Parallelism {val} exceeds maximum allowed {MAX_PARALLELISM}",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Parallelism within bounds")


@dataclass
class ZeroParallelismRule(Rule):
    name: str = "zero_parallelism"
    description: str = "Parallelism limit must not be zero"

    def check(self, pipeline) -> LintResult:
        val = getattr(pipeline, "parallelism", None)
        if val is not None and val == 0:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message="Parallelism is set to 0; pipeline tasks will never run in parallel",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Parallelism value is valid")
