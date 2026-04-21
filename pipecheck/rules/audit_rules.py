from dataclasses import dataclass
from pipecheck.rules.base import LintResult, Rule, Severity


VALID_AUDIT_LEVELS = {"none", "basic", "full", "compliance"}
MAX_AUDIT_RETENTION_DAYS = 365


class NoAuditConfigRule(Rule):
    name = "no-audit-config"
    description = "Pipeline should define an audit configuration."

    def check(self, pipeline) -> LintResult:
        audit = getattr(pipeline, "audit", None)
        if not audit:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="No audit configuration defined. Consider adding audit settings.",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Audit config present.")


class InvalidAuditLevelRule(Rule):
    name = "invalid-audit-level"
    description = "Audit level must be one of the recognised values."

    def check(self, pipeline) -> LintResult:
        audit = getattr(pipeline, "audit", None)
        if not isinstance(audit, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="No audit dict to validate.")
        level = audit.get("level")
        if level is None:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="Audit config missing 'level' key.",
            )
        if level not in VALID_AUDIT_LEVELS:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Invalid audit level '{level}'. Must be one of: {sorted(VALID_AUDIT_LEVELS)}.",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Audit level is valid.")


class AuditRetentionTooLongRule(Rule):
    name = "audit-retention-too-long"
    description = f"Audit log retention must not exceed {MAX_AUDIT_RETENTION_DAYS} days."

    def check(self, pipeline) -> LintResult:
        audit = getattr(pipeline, "audit", None)
        if not isinstance(audit, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="No audit dict to validate.")
        retention = audit.get("retention_days")
        if retention is None:
            return LintResult(rule=self.name, severity=Severity.OK, message="No retention days specified.")
        if not isinstance(retention, (int, float)) or retention <= 0:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Audit retention_days must be a positive number, got '{retention}'.",
            )
        if retention > MAX_AUDIT_RETENTION_DAYS:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Audit retention_days {retention} exceeds maximum of {MAX_AUDIT_RETENTION_DAYS}.",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Audit retention is within limits.")
