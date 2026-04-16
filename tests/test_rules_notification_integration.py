import pytest
from dataclasses import dataclass, field
from typing import List, Optional
from pipecheck.rules import run_rules
from pipecheck.rules.notification_rules import (
    NoNotificationRule,
    InvalidNotificationTypeRule,
    InvalidNotificationEventRule,
    TooManyNotificationsRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FullPipeline:
    pipeline_id: str = "my_pipeline"
    name: str = "my_pipeline"
    schedule: str = "@daily"
    tags: List[str] = field(default_factory=lambda: ["team:data"])
    notifications: Optional[List[dict]] = field(
        default_factory=lambda: [{"type": "email", "events": ["failure"]}]
    )


NOTIFICATION_RULES = [
    NoNotificationRule(),
    InvalidNotificationTypeRule(),
    InvalidNotificationEventRule(),
    TooManyNotificationsRule(),
]


def test_valid_notifications_all_pass():
    p = _FullPipeline()
    results = run_rules(p, rules=NOTIFICATION_RULES)
    assert all(r.severity == Severity.OK for r in results)


def test_missing_notifications_produces_warning():
    p = _FullPipeline(notifications=None)
    results = run_rules(p, rules=NOTIFICATION_RULES)
    severities = [r.severity for r in results]
    assert Severity.WARNING in severities


def test_invalid_type_and_event_produce_errors():
    p = _FullPipeline(
        notifications=[
            {"type": "fax", "events": ["launch"]}
        ]
    )
    results = run_rules(p, rules=[InvalidNotificationTypeRule(), InvalidNotificationEventRule()])
    assert any(r.severity == Severity.ERROR for r in results)
