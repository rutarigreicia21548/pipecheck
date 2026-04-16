import pytest
from dataclasses import dataclass, field
from typing import List, Optional
from pipecheck.rules.notification_rules import (
    NoNotificationRule,
    InvalidNotificationTypeRule,
    InvalidNotificationEventRule,
    TooManyNotificationsRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FakePipeline:
    notifications: Optional[List[dict]] = None


def test_no_notifications_returns_warning():
    p = _FakePipeline()
    result = NoNotificationRule().check(p)
    assert result.severity == Severity.WARNING


def test_empty_notifications_returns_warning():
    p = _FakePipeline(notifications=[])
    result = NoNotificationRule().check(p)
    assert result.severity == Severity.WARNING


def test_notifications_present_passes_no_notification_rule():
    p = _FakePipeline(notifications=[{"type": "email", "events": ["failure"]}])
    result = NoNotificationRule().check(p)
    assert result.severity == Severity.OK


def test_valid_notification_type_passes():
    p = _FakePipeline(notifications=[{"type": "slack", "events": ["failure"]}])
    result = InvalidNotificationTypeRule().check(p)
    assert result.severity == Severity.OK


def test_invalid_notification_type_returns_error():
    p = _FakePipeline(notifications=[{"type": "sms", "events": ["failure"]}])
    result = InvalidNotificationTypeRule().check(p)
    assert result.severity == Severity.ERROR
    assert "sms" in result.message


def test_no_notifications_passes_type_rule():
    p = _FakePipeline()
    result = InvalidNotificationTypeRule().check(p)
    assert result.severity == Severity.OK


def test_valid_notification_event_passes():
    p = _FakePipeline(notifications=[{"type": "email", "events": ["failure", "retry"]}])
    result = InvalidNotificationEventRule().check(p)
    assert result.severity == Severity.OK


def test_invalid_notification_event_returns_error():
    p = _FakePipeline(notifications=[{"type": "email", "events": ["start"]}])
    result = InvalidNotificationEventRule().check(p)
    assert result.severity == Severity.ERROR
    assert "start" in result.message


def test_within_max_notifications_passes():
    notifications = [{"type": "email", "events": ["failure"]}] * 3
    p = _FakePipeline(notifications=notifications)
    result = TooManyNotificationsRule().check(p)
    assert result.severity == Severity.OK


def test_too_many_notifications_returns_warning():
    notifications = [{"type": "email", "events": ["failure"]}] * 6
    p = _FakePipeline(notifications=notifications)
    result = TooManyNotificationsRule().check(p)
    assert result.severity == Severity.WARNING
    assert "6" in result.message


def test_custom_max_notifications():
    notifications = [{"type": "slack", "events": ["success"]}] * 3
    p = _FakePipeline(notifications=notifications)
    result = TooManyNotificationsRule(max_notifications=2).check(p)
    assert result.severity == Severity.WARNING
