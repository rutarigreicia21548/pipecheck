from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity


class NoComplianceTagRule(Rule):
    id = "no_compliance_tag"
    description = "Pipeline should declare a compliance tag (e.g. pii, hipaa, gdpr, public)"

    def check(self, pipeline) -> LintResult:
        tag = getattr(pipeline, "compliance_tag", None)
        if not tag:
            return LintResult(
                rule_id=self.id,
                severity=Severity.WARNING,
                message="No compliance tag set on pipeline.",
            )
        return LintResult(rule_id=self.id, severity=Severity.OK, message="Compliance tag present.")


VALID_COMPLIANCE_TAGS = {"pii", "hipaa", "gdpr", "sox", "public", "internal"}


class InvalidComplianceTagRule(Rule):
    id = "invalid_compliance_tag"
    description = f"Compliance tag must be one of: {', '.join(sorted(VALID_COMPLIANCE_TAGS))}"

    def check(self, pipeline) -> LintResult:
        tag = getattr(pipeline, "compliance_tag", None)
        if not tag:
            return LintResult(rule_id=self.id, severity=Severity.OK, message="No compliance tag to validate.")
        if tag.lower() not in VALID_COMPLIANCE_TAGS:
            return LintResult(
                rule_id=self.id,
                severity=Severity.ERROR,
                message=f"Invalid compliance tag '{tag}'. Must be one of: {', '.join(sorted(VALID_COMPLIANCE_TAGS))}.",
            )
        return LintResult(rule_id=self.id, severity=Severity.OK, message="Compliance tag is valid.")


class PiiWithoutOwnerRule(Rule):
    id = "pii_without_owner"
    description = "Pipelines tagged 'pii' must have an owner set."

    def check(self, pipeline) -> LintResult:
        tag = getattr(pipeline, "compliance_tag", None)
        owner = getattr(pipeline, "owner", None)
        if tag and tag.lower() == "pii" and not owner:
            return LintResult(
                rule_id=self.id,
                severity=Severity.ERROR,
                message="Pipeline tagged 'pii' must have an owner specified.",
            )
        return LintResult(rule_id=self.id, severity=Severity.OK, message="PII owner check passed.")
