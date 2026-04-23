from dataclasses import dataclass, field
from typing import Any

from pipecheck.rules.rollback_rules import ROLLBACK_RULES
from pipecheck.rules.base import Severity


@dataclass
class _FullPipeline:
    pipeline_id: str = "my_pipeline"
    name: str = "My Pipeline"
    rollback: Any = None


def _rollback_rules(pipeline):
    return [rule.check(pipeline) for rule in ROLLBACK_RULES]


def test_valid_rollback_all_pass():
    pipeline = _FullPipeline(
        rollback={"strategy": "checkpoint", "window_days": 14}
    )
    results = _rollback_rules(pipeline)
    assert all(r.passed for r in results), [
        r.message for r in results if not r.passed
    ]


def test_missing_rollback_produces_warning():
    pipeline = _FullPipeline(rollback=None)
    results = _rollback_rules(pipeline)
    failures = [r for r in results if not r.passed]
    assert len(failures) == 1
    assert failures[0].severity == Severity.WARNING


def test_invalid_strategy_produces_error():
    pipeline = _FullPipeline(rollback={"strategy": "rewind", "window_days": 5})
    results = _rollback_rules(pipeline)
    failures = [r for r in results if not r.passed]
    rule_names = [r.rule for r in failures]
    assert "invalid-rollback-strategy" in rule_names


def test_excessive_window_produces_warning():
    pipeline = _FullPipeline(rollback={"strategy": "full", "window_days": 60})
    results = _rollback_rules(pipeline)
    failures = [r for r in results if not r.passed]
    rule_names = [r.rule for r in failures]
    assert "rollback-window-too-large" in rule_names


def test_none_strategy_with_large_window_produces_only_window_warning():
    pipeline = _FullPipeline(rollback={"window_days": 45})
    results = _rollback_rules(pipeline)
    failures = [r for r in results if not r.passed]
    rule_names = [r.rule for r in failures]
    assert "rollback-window-too-large" in rule_names
    assert "invalid-rollback-strategy" not in rule_names
