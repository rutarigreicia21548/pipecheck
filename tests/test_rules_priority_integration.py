from dataclasses import dataclass, field
from typing import Optional
from pipecheck.rules.priority_rules import (
    NoPriorityRule,
    InvalidPriorityLevelRule,
    PriorityWeightTooHighRule,
)


@dataclass
class _FullPipeline:
    pipeline_id: str = "my_pipeline"
    priority: Optional[str] = None
    priority_weight: Optional[float] = None


def _priority_rules():
    return [
        NoPriorityRule(),
        InvalidPriorityLevelRule(),
        PriorityWeightTooHighRule(),
    ]


def test_valid_priority_all_pass():
    pipeline = _FullPipeline(priority="high", priority_weight=10)
    results = [rule.check(pipeline) for rule in _priority_rules()]
    assert all(r.passed for r in results), [
        r.message for r in results if not r.passed
    ]


def test_missing_priority_produces_warning():
    pipeline = _FullPipeline(priority=None)
    results = [rule.check(pipeline) for rule in _priority_rules()]
    failed = [r for r in results if not r.passed]
    assert any("priority" in r.message.lower() for r in failed)


def test_invalid_priority_level_produces_error():
    pipeline = _FullPipeline(priority="urgent", priority_weight=5)
    results = [rule.check(pipeline) for rule in _priority_rules()]
    failed = [r for r in results if not r.passed]
    assert any("urgent" in r.message for r in failed)


def test_excessive_weight_produces_error():
    pipeline = _FullPipeline(priority="low", priority_weight=500)
    results = [rule.check(pipeline) for rule in _priority_rules()]
    failed = [r for r in results if not r.passed]
    assert any("500" in r.message for r in failed)


def test_critical_priority_with_no_weight_passes_weight_rule():
    pipeline = _FullPipeline(priority="critical", priority_weight=None)
    result = PriorityWeightTooHighRule().check(pipeline)
    assert result.passed
