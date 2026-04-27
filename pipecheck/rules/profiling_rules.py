from __future__ import annotations
from pipecheck.rules.base import LintResult, Rule, Severity

VALID_PROFILING_BACKENDS = {"datadog", "opentelemetry", "prometheus", "custom", "none"}
VALID_SAMPLE_UNITS = {"percent", "rows", "bytes"}
MAX_SAMPLE_RATE = 100
MAX_PROFILE_RETENTION_DAYS = 365


class NoProfilingConfigRule(Rule):
    name = "no-profiling-config"
    description = "Pipeline should define a profiling configuration."

    def check(self, pipeline) -> LintResult:
        profiling = getattr(pipeline, "profiling", None)
        if not profiling:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="No profiling configuration defined; consider adding one for observability.",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Profiling config present.")


class InvalidProfilingBackendRule(Rule):
    name = "invalid-profiling-backend"
    description = "Profiling backend must be one of the recognised values."

    def check(self, pipeline) -> LintResult:
        profiling = getattr(pipeline, "profiling", None)
        if not isinstance(profiling, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="No profiling dict to validate.")
        backend = profiling.get("backend", "").lower()
        if backend and backend not in VALID_PROFILING_BACKENDS:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Invalid profiling backend '{backend}'. Must be one of: {sorted(VALID_PROFILING_BACKENDS)}.",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Profiling backend is valid.")


class SampleRateTooHighRule(Rule):
    name = "sample-rate-too-high"
    description = "Profiling sample rate must not exceed 100 percent."

    def check(self, pipeline) -> LintResult:
        profiling = getattr(pipeline, "profiling", None)
        if not isinstance(profiling, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="No profiling dict to validate.")
        rate = profiling.get("sample_rate")
        if rate is not None and rate > MAX_SAMPLE_RATE:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Sample rate {rate} exceeds maximum allowed ({MAX_SAMPLE_RATE}).",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Sample rate is within bounds.")


class ProfilingRetentionTooLongRule(Rule):
    name = "profiling-retention-too-long"
    description = f"Profiling data retention must not exceed {MAX_PROFILE_RETENTION_DAYS} days."

    def check(self, pipeline) -> LintResult:
        profiling = getattr(pipeline, "profiling", None)
        if not isinstance(profiling, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="No profiling dict to validate.")
        retention = profiling.get("retention_days")
        if retention is not None and retention > MAX_PROFILE_RETENTION_DAYS:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message=f"Profiling retention {retention} days exceeds recommended max ({MAX_PROFILE_RETENTION_DAYS}).",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Profiling retention is acceptable.")
