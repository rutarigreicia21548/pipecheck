from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity


class NoAlertRule(Rule):
    id = "no-alert"
    description = "Pipeline should define at least one alert/notification."
    severity = Severity.WARNING

    def check(self, pipeline) -> LintResult:
        alerts = getattr(pipeline, "alerts", None)
        if not alerts:
            return LintResult(
                rule_id=self.id,
                severity=self.severity,
                message="No alerts configured. Consider adding on-failure notifications.",
                pipeline_id=getattr(pipeline, "id", None) or getattr(pipeline, "name", None),
            )
        return LintResult(rule_id=self.id, passed=True)


class InvalidAlertChannelRule(Rule):
    id = "invalid-alert-channel"
    description = "Alert channels must be one of: email, slack, pagerduty, webhook."
    severity = Severity.ERROR
    VALID_CHANNELS = {"email", "slack", "pagerduty", "webhook"}

    def check(self, pipeline) -> LintResult:
        alerts = getattr(pipeline, "alerts", None) or []
        invalid = [a for a in alerts if a not in self.VALID_CHANNELS]
        if invalid:
            return LintResult(
                rule_id=self.id,
                severity=self.severity,
                message=f"Invalid alert channel(s): {invalid}. Must be one of {sorted(self.VALID_CHANNELS)}.",
                pipeline_id=getattr(pipeline, "id", None) or getattr(pipeline, "name", None),
            )
        return LintResult(rule_id=self.id, passed=True)


class TooManyAlertsRule(Rule):
    id = "too-many-alerts"
    description = "Pipeline should not define more than 5 alert channels."
    severity = Severity.WARNING
    MAX_ALERTS = 5

    def check(self, pipeline) -> LintResult:
        alerts = getattr(pipeline, "alerts", None) or []
        if len(alerts) > self.MAX_ALERTS:
            return LintResult(
                rule_id=self.id,
                severity=self.severity,
                message=f"Too many alert channels ({len(alerts)}). Maximum recommended is {self.MAX_ALERTS}.",
                pipeline_id=getattr(pipeline, "id", None) or getattr(pipeline, "name", None),
            )
        return LintResult(rule_id=self.id, passed=True)
