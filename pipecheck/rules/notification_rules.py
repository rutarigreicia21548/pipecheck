from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity


VALID_NOTIFICATION_EVENTS = {"failure", "success", "retry", "sla_miss"}
VALID_NOTIFICATION_TYPES = {"email", "slack", "pagerduty", "webhook"}


@dataclass
class NoNotificationRule(Rule):
    name: str = "no_notification"
    description: str = "Pipeline should define at least one notification"

    def check(self, pipeline) -> LintResult:
        notifications = getattr(pipeline, "notifications", None)
        if not notifications:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="No notifications defined for pipeline",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")


@dataclass
class InvalidNotificationTypeRule(Rule):
    name: str = "invalid_notification_type"
    description: str = "Notification types must be from the allowed set"

    def check(self, pipeline) -> LintResult:
        notifications = getattr(pipeline, "notifications", None) or []
        for n in notifications:
            ntype = n.get("type") if isinstance(n, dict) else None
            if ntype not in VALID_NOTIFICATION_TYPES:
                return LintResult(
                    rule=self.name,
                    severity=Severity.ERROR,
                    message=f"Invalid notification type '{ntype}'; allowed: {VALID_NOTIFICATION_TYPES}",
                )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")


@dataclass
class InvalidNotificationEventRule(Rule):
    name: str = "invalid_notification_event"
    description: str = "Notification events must be from the allowed set"

    def check(self, pipeline) -> LintResult:
        notifications = getattr(pipeline, "notifications", None) or []
        for n in notifications:
            if not isinstance(n, dict):
                continue
            events = n.get("events", [])
            for event in events:
                if event not in VALID_NOTIFICATION_EVENTS:
                    return LintResult(
                        rule=self.name,
                        severity=Severity.ERROR,
                        message=f"Invalid notification event '{event}'; allowed: {VALID_NOTIFICATION_EVENTS}",
                    )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")


@dataclass
class TooManyNotificationsRule(Rule):
    name: str = "too_many_notifications"
    description: str = "Pipeline should not define more than 5 notifications"
    max_notifications: int = 5

    def check(self, pipeline) -> LintResult:
        notifications = getattr(pipeline, "notifications", None) or []
        if len(notifications) > self.max_notifications:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message=f"Too many notifications ({len(notifications)}); max recommended is {self.max_notifications}",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")
