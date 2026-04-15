from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity


@dataclass
class NoOwnerRule(Rule):
    name: str = "no-owner"
    description: str = "Pipeline should have an owner defined"
    severity: Severity = Severity.WARNING

    def check(self, pipeline) -> LintResult:
        owner = getattr(pipeline, "owner", None)
        if not owner:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message="Pipeline has no owner defined",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)


@dataclass
class InvalidOwnerFormatRule(Rule):
    name: str = "invalid-owner-format"
    description: str = "Owner should be a non-empty string without special characters"
    severity: Severity = Severity.ERROR

    _ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-@ ")

    def check(self, pipeline) -> LintResult:
        owner = getattr(pipeline, "owner", None)
        if not owner:
            return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
        if not isinstance(owner, str) or not owner.strip():
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message="Owner must be a non-empty string",
                passed=False,
            )
        invalid = [c for c in owner if c not in self._ALLOWED_CHARS]
        if invalid:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=f"Owner contains invalid characters: {invalid}",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)


@dataclass
class GenericOwnerRule(Rule):
    name: str = "generic-owner"
    description: str = "Owner should not be a generic placeholder value"
    severity: Severity = Severity.WARNING

    _GENERIC_OWNERS = {"airflow", "prefect", "admin", "default", "unknown", "user", "owner"}

    def check(self, pipeline) -> LintResult:
        owner = getattr(pipeline, "owner", None)
        if not owner:
            return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
        if owner.strip().lower() in self._GENERIC_OWNERS:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=f"Owner '{owner}' is a generic placeholder; use a real team or person",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
