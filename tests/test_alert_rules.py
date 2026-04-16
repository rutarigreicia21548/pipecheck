import pytest
from dataclasses import dataclass, field
from typing import Optional, List
from pipecheck.rules.alert_rules import NoAlertRule, InvalidAlertChannelRule, TooManyAlertsRule
from pipecheck.rules.base import Severity


@dataclass
class _FakePipeline:
    id: Optional[str] = "my_pipeline"
    alerts: Optional[List[str]] = None

    def __post_init__(self):
        pass


def test_no_alerts_returns_warning():
    p = _FakePipeline(alerts=None)
    result = NoAlertRule().check(p)
    assert not result.passed
    assert result.severity == Severity.WARNING


def test_empty_alerts_returns_warning():
    p = _FakePipeline(alerts=[])
    result = NoAlertRule().check(p)
    assert not result.passed


def test_alerts_present_passes_no_alert_rule():
    p = _FakePipeline(alerts=["email"])
    result = NoAlertRule().check(p)
    assert result.passed


def test_valid_channels_pass_invalid_channel_rule():
    p = _FakePipeline(alerts=["slack", "email"])
    result = InvalidAlertChannelRule().check(p)
    assert result.passed


def test_invalid_channel_returns_error():
    p = _FakePipeline(alerts=["teams"])
    result = InvalidAlertChannelRule().check(p)
    assert not result.passed
    assert result.severity == Severity.ERROR
    assert "teams" in result.message


def test_mixed_valid_invalid_channels_fails():
    p = _FakePipeline(alerts=["slack", "discord"])
    result = InvalidAlertChannelRule().check(p)
    assert not result.passed
    assert "discord" in result.message


def test_no_alerts_passes_invalid_channel_rule():
    p = _FakePipeline(alerts=None)
    result = InvalidAlertChannelRule().check(p)
    assert result.passed


def test_within_limit_passes_too_many_alerts_rule():
    p = _FakePipeline(alerts=["slack", "email"])
    result = TooManyAlertsRule().check(p)
    assert result.passed


def test_exceeding_limit_returns_warning():
    p = _FakePipeline(alerts=["slack", "email", "pagerduty", "webhook", "slack", "email"])
    result = TooManyAlertsRule().check(p)
    assert not result.passed
    assert result.severity == Severity.WARNING
    assert "6" in result.message


def test_exactly_at_limit_passes():
    p = _FakePipeline(alerts=["slack", "email", "pagerduty", "webhook", "slack"])
    result = TooManyAlertsRule().check(p)
    assert result.passed
