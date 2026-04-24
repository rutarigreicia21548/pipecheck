import pytest
from dataclasses import dataclass, field
from pipecheck.rules.trigger_rules import NoTriggerRule, InvalidTriggerTypeRule, TooManyTriggerConditionsRule
from pipecheck.rules.base import Severity


@dataclass
class _FullPipeline:
    dag_id: str = "my_pipeline"
    trigger: object = None


def _trigger_rules():
    return [NoTriggerRule(), InvalidTriggerTypeRule(), TooManyTriggerConditionsRule()]


def _check_all(trigger):
    """Helper that creates a pipeline with the given trigger and runs all trigger rules."""
    p = _FullPipeline(trigger=trigger)
    return [r.check(p) for r in _trigger_rules()]


def test_valid_trigger_all_pass():
    results = _check_all({"type": "scheduled", "conditions": ["weekday"]})
    assert all(r.severity in (Severity.OK,) for r in results)


def test_missing_trigger_produces_warning():
    results = _check_all(None)
    severities = [r.severity for r in results]
    assert Severity.WARNING in severities


def test_invalid_trigger_type_produces_error():
    results = _check_all({"type": "bad_type", "conditions": []})
    severities = [r.severity for r in results]
    assert Severity.ERROR in severities


def test_too_many_trigger_conditions_produces_error():
    """A trigger with an excessive number of conditions should produce an ERROR."""
    many_conditions = [f"condition_{i}" for i in range(20)]
    results = _check_all({"type": "scheduled", "conditions": many_conditions})
    severities = [r.severity for r in results]
    assert Severity.ERROR in severities


def test_empty_conditions_list_is_valid():
    """A trigger with a valid type but no conditions should still pass all rules."""
    results = _check_all({"type": "scheduled", "conditions": []})
    assert all(r.severity in (Severity.OK,) for r in results)
