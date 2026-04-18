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


def test_valid_trigger_all_pass():
    p = _FullPipeline(trigger={"type": "scheduled", "conditions": ["weekday"]})
    results = [r.check(p) for r in _trigger_rules()]
    assert all(r.severity in (Severity.OK,) for r in results)


def test_missing_trigger_produces_warning():
    p = _FullPipeline(trigger=None)
    results = [r.check(p) for r in _trigger_rules()]
    severities = [r.severity for r in results]
    assert Severity.WARNING in severities


def test_invalid_trigger_type_produces_error():
    p = _FullPipeline(trigger={"type": "bad_type", "conditions": []})
    results = [r.check(p) for r in _trigger_rules()]
    severities = [r.severity for r in results]
    assert Severity.ERROR in severities


def test_too_many_trigger_conditions_produces_error():
    """A trigger with an excessive number of conditions should produce an ERROR."""
    many_conditions = [f"condition_{i}" for i in range(20)]
    p = _FullPipeline(trigger={"type": "scheduled", "conditions": many_conditions})
    results = [r.check(p) for r in _trigger_rules()]
    severities = [r.severity for r in results]
    assert Severity.ERROR in severities
