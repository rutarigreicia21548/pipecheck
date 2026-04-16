from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity


@dataclass
class NoDescriptionRule(Rule):
    name: str = "no-description"
    description: str = "Pipeline should have a description or docstring."
    severity: Severity = Severity.WARNING

    def check(self, pipeline) -> LintResult:
        doc = getattr(pipeline, "description", None)
        if not doc or not str(doc).strip():
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message="Pipeline has no description.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)


@dataclass
class ShortDescriptionRule(Rule):
    name: str = "short-description"
    description: str = "Pipeline description should be at least 10 characters."
    severity: Severity = Severity.WARNING
    min_length: int = 10

    def check(self, pipeline) -> LintResult:
        doc = getattr(pipeline, "description", None)
        if doc and len(str(doc).strip()) >= self.min_length:
            return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
        return LintResult(
            rule=self.name,
            severity=self.severity,
            message=f"Pipeline description is too short (min {self.min_length} chars).",
            passed=False,
        )


@dataclass
class NoOwnerContactRule(Rule):
    name: str = "no-owner-contact"
    description: str = "Description should contain an email or contact reference."
    severity: Severity = Severity.INFO

    def check(self, pipeline) -> LintResult:
        doc = getattr(pipeline, "description", "") or ""
        if "@" in doc:
            return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
        return LintResult(
            rule=self.name,
            severity=self.severity,
            message="Description does not contain a contact email.",
            passed=False,
        )
