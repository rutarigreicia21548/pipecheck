from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity

VALID_LABEL_PATTERN = r'^[a-z][a-z0-9_\-]*$'
MAX_LABELS = 10
RESERVED_LABELS = {"internal", "deprecated", "experimental"}


@dataclass
class NoLabelsRule(Rule):
    name: str = "no-labels"
    description: str = "Pipeline should have at least one label"

    def check(self, pipeline) -> LintResult:
        labels = getattr(pipeline, "labels", None)
        if not labels:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="Pipeline has no labels defined",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Labels present")


@dataclass
class TooManyLabelsRule(Rule):
    name: str = "too-many-labels"
    description: str = f"Pipeline should not have more than {MAX_LABELS} labels"

    def check(self, pipeline) -> LintResult:
        labels = getattr(pipeline, "labels", None) or []
        if len(labels) > MAX_LABELS:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Pipeline has {len(labels)} labels; max allowed is {MAX_LABELS}",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Label count within limit")


@dataclass
class InvalidLabelFormatRule(Rule):
    name: str = "invalid-label-format"
    description: str = "Labels must be lowercase alphanumeric with hyphens or underscores"

    def check(self, pipeline) -> LintResult:
        import re
        labels = getattr(pipeline, "labels", None) or []
        bad = [l for l in labels if not re.match(VALID_LABEL_PATTERN, l)]
        if bad:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Invalid label format(s): {bad}",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="All labels valid")


@dataclass
class ReservedLabelRule(Rule):
    name: str = "reserved-label"
    description: str = "Pipeline should not use reserved labels without explicit intent"

    def check(self, pipeline) -> LintResult:
        labels = set(getattr(pipeline, "labels", None) or [])
        used = labels & RESERVED_LABELS
        if used:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message=f"Reserved label(s) in use: {sorted(used)}",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="No reserved labels used")
