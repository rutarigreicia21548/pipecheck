from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity
import re


class NoVersionRule(Rule):
    id = "no-version"
    description = "Pipeline should declare a version."

    def check(self, pipeline) -> LintResult:
        v = getattr(pipeline, "version", None)
        if not v:
            return LintResult(
                rule_id=self.id,
                severity=Severity.WARNING,
                message="Pipeline has no version specified.",
            )
        return LintResult(rule_id=self.id, severity=Severity.OK, message="Version present.")


class InvalidVersionFormatRule(Rule):
    id = "invalid-version-format"
    description = "Pipeline version should follow semver (e.g. 1.0.0)."
    _pattern = re.compile(r"^\d+\.\d+\.\d+$")

    def check(self, pipeline) -> LintResult:
        v = getattr(pipeline, "version", None)
        if not v:
            return LintResult(rule_id=self.id, severity=Severity.OK, message="No version to validate.")
        if not self._pattern.match(str(v)):
            return LintResult(
                rule_id=self.id,
                severity=Severity.ERROR,
                message=f"Version '{v}' does not follow semver format (MAJOR.MINOR.PATCH).",
            )
        return LintResult(rule_id=self.id, severity=Severity.OK, message="Version format valid.")


class MajorVersionZeroRule(Rule):
    id = "major-version-zero"
    description = "Major version 0 indicates an unstable/pre-release pipeline."

    def check(self, pipeline) -> LintResult:
        v = getattr(pipeline, "version", None)
        if not v:
            return LintResult(rule_id=self.id, severity=Severity.OK, message="No version to validate.")
        parts = str(v).split(".")
        if parts[0] == "0":
            return LintResult(
                rule_id=self.id,
                severity=Severity.WARNING,
                message=f"Pipeline version '{v}' has major version 0, indicating pre-release.",
            )
        return LintResult(rule_id=self.id, severity=Severity.OK, message="Major version is stable.")
