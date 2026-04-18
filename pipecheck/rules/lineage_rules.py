from dataclasses import dataclass
from typing import Any
from pipecheck.rules.base import LintResult, Rule, Severity


class NoLineageRule(Rule):
    id = "no-lineage"
    description = "Pipeline should declare input/output lineage."
    severity = Severity.WARNING

    def check(self, pipeline: Any) -> LintResult:
        lineage = getattr(pipeline, "lineage", None)
        if not lineage:
            return LintResult(
                rule_id=self.id,
                severity=self.severity,
                message="No lineage declared. Add 'lineage' with inputs/outputs.",
                passed=False,
            )
        return LintResult(rule_id=self.id, severity=self.severity, message="OK", passed=True)


class MissingLineageInputsRule(Rule):
    id = "missing-lineage-inputs"
    description = "Lineage block should define at least one input source."
    severity = Severity.WARNING

    def check(self, pipeline: Any) -> LintResult:
        lineage = getattr(pipeline, "lineage", None) or {}
        inputs = lineage.get("inputs") if isinstance(lineage, dict) else None
        if not inputs:
            return LintResult(
                rule_id=self.id,
                severity=self.severity,
                message="Lineage has no inputs defined.",
                passed=False,
            )
        return LintResult(rule_id=self.id, severity=self.severity, message="OK", passed=True)


class MissingLineageOutputsRule(Rule):
    id = "missing-lineage-outputs"
    description = "Lineage block should define at least one output destination."
    severity = Severity.WARNING

    def check(self, pipeline: Any) -> LintResult:
        lineage = getattr(pipeline, "lineage", None) or {}
        outputs = lineage.get("outputs") if isinstance(lineage, dict) else None
        if not outputs:
            return LintResult(
                rule_id=self.id,
                severity=self.severity,
                message="Lineage has no outputs defined.",
                passed=False,
            )
        return LintResult(rule_id=self.id, severity=self.severity, message="OK", passed=True)


class InvalidLineageDatasetRule(Rule):
    id = "invalid-lineage-dataset"
    description = "Lineage dataset names must be non-empty strings."
    severity = Severity.ERROR

    def check(self, pipeline: Any) -> LintResult:
        lineage = getattr(pipeline, "lineage", None) or {}
        if not isinstance(lineage, dict):
            return LintResult(rule_id=self.id, severity=self.severity, message="OK", passed=True)
        all_datasets = list(lineage.get("inputs", []) or []) + list(lineage.get("outputs", []) or [])
        for ds in all_datasets:
            if not isinstance(ds, str) or not ds.strip():
                return LintResult(
                    rule_id=self.id,
                    severity=self.severity,
                    message=f"Invalid dataset entry in lineage: {ds!r}. Must be a non-empty string.",
                    passed=False,
                )
        return LintResult(rule_id=self.id, severity=self.severity, message="OK", passed=True)
