from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity


VALID_CHECK_TYPES = {"not_null", "unique", "accepted_values", "range", "regex", "custom"}
MAX_QUALITY_CHECKS = 20


class NoDataQualityChecksRule(Rule):
    name = "no_data_quality_checks"
    description = "Pipeline should define at least one data quality check."

    def check(self, pipeline) -> LintResult:
        checks = getattr(pipeline, "data_quality_checks", None)
        if not checks:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="No data quality checks defined.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=Severity.WARNING, message="OK", passed=True)


class InvalidCheckTypeRule(Rule):
    name = "invalid_check_type"
    description = "All data quality check types must be valid."

    def check(self, pipeline) -> LintResult:
        checks = getattr(pipeline, "data_quality_checks", None) or []
        invalid = [c for c in checks if c not in VALID_CHECK_TYPES]
        if invalid:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Invalid data quality check type(s): {invalid}. Valid: {sorted(VALID_CHECK_TYPES)}",
                passed=False,
            )
        return LintResult(rule=self.name, severity=Severity.ERROR, message="OK", passed=True)


class TooManyChecksRule(Rule):
    name = "too_many_data_quality_checks"
    description = f"Pipeline should not define more than {MAX_QUALITY_CHECKS} data quality checks."

    def check(self, pipeline) -> LintResult:
        checks = getattr(pipeline, "data_quality_checks", None) or []
        if len(checks) > MAX_QUALITY_CHECKS:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message=f"Too many data quality checks: {len(checks)} (max {MAX_QUALITY_CHECKS}).",
                passed=False,
            )
        return LintResult(rule=self.name, severity=Severity.WARNING, message="OK", passed=True)
