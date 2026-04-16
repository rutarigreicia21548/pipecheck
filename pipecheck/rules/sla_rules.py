from pipecheck.rules.base import Rule, LintResult, Severity


class NoSLARule(Rule):
    id = "no-sla"
    description = "Pipeline should define an SLA (max expected duration in seconds)."
    severity = Severity.WARNING

    def check(self, pipeline) -> LintResult:
        sla = getattr(pipeline, "sla", None)
        if sla is None:
            return LintResult(
                rule_id=self.id,
                severity=self.severity,
                message="No SLA defined. Consider setting a maximum expected runtime.",
                pipeline_id=getattr(pipeline, "id", None) or getattr(pipeline, "name", None),
            )
        return LintResult(rule_id=self.id, passed=True)


class SLATooLongRule(Rule):
    id = "sla-too-long"
    description = "SLA should not exceed 86400 seconds (24 hours)."
    severity = Severity.WARNING
    MAX_SLA = 86400

    def check(self, pipeline) -> LintResult:
        sla = getattr(pipeline, "sla", None)
        if sla is not None and sla > self.MAX_SLA:
            return LintResult(
                rule_id=self.id,
                severity=self.severity,
                message=f"SLA of {sla}s exceeds maximum recommended {self.MAX_SLA}s (24h).",
                pipeline_id=getattr(pipeline, "id", None) or getattr(pipeline, "name", None),
            )
        return LintResult(rule_id=self.id, passed=True)


class ZeroSLARule(Rule):
    id = "zero-sla"
    description = "SLA must be greater than zero."
    severity = Severity.ERROR

    def check(self, pipeline) -> LintResult:
        sla = getattr(pipeline, "sla", None)
        if sla is not None and sla <= 0:
            return LintResult(
                rule_id=self.id,
                severity=self.severity,
                message=f"SLA must be a positive number, got {sla}.",
                pipeline_id=getattr(pipeline, "id", None) or getattr(pipeline, "name", None),
            )
        return LintResult(rule_id=self.id, passed=True)
