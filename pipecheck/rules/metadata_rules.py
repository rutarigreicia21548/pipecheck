from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity


class NoMetadataRule(Rule):
    id = "no-metadata"
    description = "Pipeline should define a metadata dict."

    def check(self, pipeline) -> LintResult:
        meta = getattr(pipeline, "metadata", None)
        if not meta:
            return LintResult(
                rule_id=self.id,
                severity=Severity.WARNING,
                message="Pipeline has no metadata defined.",
            )
        return LintResult(rule_id=self.id, severity=Severity.OK, message="OK")


class InvalidMetadataTypeRule(Rule):
    id = "invalid-metadata-type"
    description = "Metadata must be a dict."

    def check(self, pipeline) -> LintResult:
        meta = getattr(pipeline, "metadata", None)
        if meta is not None and not isinstance(meta, dict):
            return LintResult(
                rule_id=self.id,
                severity=Severity.ERROR,
                message=f"Metadata must be a dict, got {type(meta).__name__}.",
            )
        return LintResult(rule_id=self.id, severity=Severity.OK, message="OK")


class EmptyMetadataRule(Rule):
    id = "empty-metadata"
    description = "Metadata dict should not be empty."

    def check(self, pipeline) -> LintResult:
        meta = getattr(pipeline, "metadata", None)
        if isinstance(meta, dict) and len(meta) == 0:
            return LintResult(
                rule_id=self.id,
                severity=Severity.WARNING,
                message="Metadata dict is empty.",
            )
        return LintResult(rule_id=self.id, severity=Severity.OK, message="OK")


class ReservedMetadataKeyRule(Rule):
    id = "reserved-metadata-key"
    description = "Metadata must not use reserved keys: 'id', 'name', 'version'."
    RESERVED = {"id", "name", "version"}

    def check(self, pipeline) -> LintResult:
        meta = getattr(pipeline, "metadata", None)
        if not isinstance(meta, dict):
            return LintResult(rule_id=self.id, severity=Severity.OK, message="OK")
        bad = self.RESERVED & meta.keys()
        if bad:
            return LintResult(
                rule_id=self.id,
                severity=Severity.ERROR,
                message=f"Metadata uses reserved keys: {sorted(bad)}.",
            )
        return LintResult(rule_id=self.id, severity=Severity.OK, message="OK")
