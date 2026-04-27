from dataclasses import dataclass
from pipecheck.rules.base import LintResult, Rule, Severity

MAX_RUNTIME_HOURS = 24
WARN_RUNTIME_HOURS = 8


def _parse_runtime(runtime):
    """Attempt to parse runtime as a float number of hours.

    Returns (float, None) on success or (None, LintResult) if parsing fails,
    allowing callers to return the error result immediately.
    """
    try:
        return float(runtime), None
    except (TypeError, ValueError):
        return None, None  # caller decides how to handle non-numeric


@dataclass
class NoRuntimeLimitRule(Rule):
    name: str = "no_runtime_limit"
    description: str = "Pipeline should define an expected max runtime"

    def check(self, pipeline) -> LintResult:
        runtime = getattr(pipeline, "max_runtime", None)
        if runtime is None:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="No max_runtime defined; consider setting an expected upper bound",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="max_runtime is set")


@dataclass
class RuntimeTooLongRule(Rule):
    name: str = "runtime_too_long"
    description: str = f"Pipeline max_runtime must not exceed {MAX_RUNTIME_HOURS} hours"

    def check(self, pipeline) -> LintResult:
        runtime = getattr(pipeline, "max_runtime", None)
        if runtime is None:
            return LintResult(rule=self.name, severity=Severity.OK, message="No max_runtime to validate")
        try:
            value = float(runtime)
        except (TypeError, ValueError):
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"max_runtime '{runtime}' is not a valid number",
            )
        if value > MAX_RUNTIME_HOURS:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"max_runtime {value}h exceeds maximum allowed {MAX_RUNTIME_HOURS}h",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="max_runtime is within limits")


@dataclass
class RuntimeWarnThresholdRule(Rule):
    name: str = "runtime_warn_threshold"
    description: str = f"Pipeline max_runtime over {WARN_RUNTIME_HOURS}h should be reviewed"

    def check(self, pipeline) -> LintResult:
        runtime = getattr(pipeline, "max_runtime", None)
        if runtime is None:
            return LintResult(rule=self.name, severity=Severity.OK, message="No max_runtime to validate")
        try:
            value = float(runtime)
        except (TypeError, ValueError):
            return LintResult(rule=self.name, severity=Severity.OK, message="max_runtime is not numeric; skipping threshold check")
        if value > WARN_RUNTIME_HOURS:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message=f"max_runtime {value}h exceeds warning threshold of {WARN_RUNTIME_HOURS}h; ensure this is intentional",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="max_runtime is below warning threshold")
