import pytest
from dataclasses import dataclass, field
from pipecheck.rules.trigger_rules import NoTriggerRule, InvalidTriggerTypeRule, TooManyTriggerConditionsRule
from pipecheck.rules.base import Severity


@dataclass
class _FakePipeline:
    trigger: object = None


def test_no_trigger_returns_warning():
    p = _FakePipeline(trigger=None)
    result = NoTriggerRule().check(p)
    assert result.severity == Severity.WARNING


def test_trigger_present_passes_no_trigger_rule():
    p = _FakePipeline(trigger="scheduled")
    result = NoTriggerRule().check(p)
    assert result.severity == Severity.OK


def test_trigger_dict_present_passes_no_trigger_rule():
    p = _FakePipeline(trigger={"type": "event"})
    result = NoTriggerRule().check(p)
    assert result.severity == Severity.OK


def test_valid_trigger_types_pass_invalid_rule():
    for t in ("manual", "scheduled", "event", "sensor", "webhook"):
        p = _FakePipeline(trigger=t)
        result = InvalidTriggerTypeRule().check(p)
        assert result.severity == Severity.OK


def test_invalid_trigger_type_returns_error():
    p = _FakePipeline(trigger="cron")
    result = InvalidTriggerTypeRule().check(p)
    assert result.severity == Severity.ERROR
    assert "cron" in result.message


def test_invalid_trigger_type_in_dict_returns_error():
    p = _FakePipeline(trigger={"type": "unknown"})
    result = InvalidTriggerTypeRule().check(p)
    assert result.severity == Severity.ERROR


def test_no_trigger_skips_invalid_type_rule():
    p = _FakePipeline(trigger=None)
    result = InvalidTriggerTypeRule().check(p)
    assert result.severity == Severity.OK


def test_few_conditions_passes_too_many_rule():
    p = _FakePipeline(trigger={"type": "event", "conditions": ["a", "b", "c"]})
    result = TooManyTriggerConditionsRule().check(p)
    assert result.severity == Severity.OK


def test_too_many_conditions_returns_warning():
    conditions = [f"cond_{i}" for i in range(15)]
    p = _FakePipeline(trigger={"type": "event", "conditions": conditions})
    result = TooManyTriggerConditionsRule().check(p)
    assert result.severity == Severity.WARNING
    assert "15" in result.message


def test_string_trigger_skips_conditions_rule():
    p = _FakePipeline(trigger="manual")
    result = TooManyTriggerConditionsRule().check(p)
    assert result.severity == Severity.OK


def test_no_trigger_skips_conditions_rule():
    p = _FakePipeline(trigger=None)
    result = TooManyTriggerConditionsRule().check(p)
    assert result.severity == Severity.OK
