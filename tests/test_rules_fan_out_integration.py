from dataclasses import dataclass, field
from typing import Any, Optional

from pipecheck.rules.fan_out_rules import (
    FanInTooHighRule,
    FanOutTooHighRule,
    InvalidFanOutStrategyRule,
    NoFanOutConfigRule,
)


@dataclass
class _FullPipeline:
    pipeline_id: str = "my_pipeline"
    name: str = "My Pipeline"
    fan_out: Optional[Any] = None


_FAN_OUT_RULES = [
    NoFanOutConfigRule(),
    FanOutTooHighRule(),
    FanInTooHighRule(),
    InvalidFanOutStrategyRule(),
]


def _run(pipeline):
    return [rule.check(pipeline) for rule in _FAN_OUT_RULES]


def test_valid_fan_out_all_pass():
    pipeline = _FullPipeline(
        fan_out={"strategy": "scatter", "degree": 4, "fan_in": 4}
    )
    results = _run(pipeline)
    failures = [r for r in results if not r.passed]
    assert not failures, [r.message for r in failures]


def test_missing_fan_out_produces_warning():
    pipeline = _FullPipeline(fan_out=None)
    results = _run(pipeline)
    failures = [r for r in results if not r.passed]
    assert len(failures) == 1
    assert failures[0].severity.name == "WARNING"


def test_excessive_degree_produces_error():
    pipeline = _FullPipeline(
        fan_out={"strategy": "broadcast", "degree": 20, "fan_in": 2}
    )
    results = _run(pipeline)
    failures = [r for r in results if not r.passed]
    assert any(r.rule == "fan-out-too-high" for r in failures)


def test_invalid_strategy_and_high_fan_in_produce_errors():
    pipeline = _FullPipeline(
        fan_out={"strategy": "explode", "degree": 3, "fan_in": 99}
    )
    results = _run(pipeline)
    failed_rules = {r.rule for r in results if not r.passed}
    assert "invalid-fan-out-strategy" in failed_rules
    assert "fan-in-too-high" in failed_rules
