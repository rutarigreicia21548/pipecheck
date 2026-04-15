"""Tests for schedule-related lint rules."""

from __future__ import annotations

import pytest
from dataclasses import dataclass, field
from typing import Optional

from pipecheck.rules.base import Severity
from pipecheck.rules.schedule_rules import (
    FrequentScheduleRule,
    InvalidCronScheduleRule,
    NoScheduleRule,
)


@dataclass
class _FakePipeline:
    id: Optional[str] = None
    name: Optional[str] = None
    schedule: Optional[str] = None

    def __post_init__(self):
        if self.id is None and self.name is None:
            self.name = "unnamed"


# ---------------------------------------------------------------------------
# NoScheduleRule
# ---------------------------------------------------------------------------

def test_no_schedule_returns_warning():
    rule = NoScheduleRule()
    result = rule.check(_FakePipeline(id="my_dag"))
    assert result is not None
    assert result.severity == Severity.WARNING
    assert "no schedule" in result.message.lower()


def test_schedule_present_passes_no_schedule_rule():
    rule = NoScheduleRule()
    result = rule.check(_FakePipeline(id="my_dag", schedule="@daily"))
    assert result is None


# ---------------------------------------------------------------------------
# InvalidCronScheduleRule
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("schedule", [
    "@daily", "@hourly", "@weekly", "@monthly", "@once", "@continuous",
])
def test_preset_schedules_are_valid(schedule):
    rule = InvalidCronScheduleRule()
    result = rule.check(_FakePipeline(id="dag", schedule=schedule))
    assert result is None


@pytest.mark.parametrize("cron", [
    "0 6 * * *",
    "*/15 * * * *",
    "0 0 1 * *",
    "30 8 * * 1-5",
])
def test_valid_cron_passes(cron):
    rule = InvalidCronScheduleRule()
    result = rule.check(_FakePipeline(id="dag", schedule=cron))
    assert result is None


@pytest.mark.parametrize("bad_cron", [
    "every day",
    "0 6 *",
    "not-a-cron",
    "60 25 * * *",  # structurally wrong field count is fine but bad values
])
def test_invalid_cron_returns_error(bad_cron):
    rule = InvalidCronScheduleRule()
    result = rule.check(_FakePipeline(id="dag", schedule=bad_cron))
    assert result is not None
    assert result.severity == Severity.ERROR
    assert bad_cron in result.message


def test_no_schedule_skipped_by_cron_rule():
    rule = InvalidCronScheduleRule()
    assert rule.check(_FakePipeline(id="dag")) is None


# ---------------------------------------------------------------------------
# FrequentScheduleRule
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("cron", ["*/1 * * * *", "*/2 * * * *", "*/4 * * * *"])
def test_too_frequent_schedule_warns(cron):
    rule = FrequentScheduleRule()
    result = rule.check(_FakePipeline(id="dag", schedule=cron))
    assert result is not None
    assert result.severity == Severity.WARNING


@pytest.mark.parametrize("cron", ["*/5 * * * *", "*/10 * * * *", "0 * * * *"])
def test_acceptable_frequency_passes(cron):
    rule = FrequentScheduleRule()
    result = rule.check(_FakePipeline(id="dag", schedule=cron))
    assert result is None


def test_frequent_rule_ignores_preset():
    rule = FrequentScheduleRule()
    assert rule.check(_FakePipeline(id="dag", schedule="@hourly")) is None
