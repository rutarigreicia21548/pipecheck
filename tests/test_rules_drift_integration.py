from pipecheck.rules.drift_rules import (
    DriftThresholdTooHighRule,
    InvalidDriftStrategyRule,
    NoDriftConfigRule,
)


class _FullPipeline:
    def __init__(self, drift=None):
        self.drift = drift


_DRIFT_RULES = [
    NoDriftConfigRule(),
    InvalidDriftStrategyRule(),
    DriftThresholdTooHighRule(),
]


def _run(pipeline):
    return [rule.check(pipeline) for rule in _DRIFT_RULES]


def test_valid_drift_all_pass():
    pipeline = _FullPipeline(drift={"strategy": "alert", "threshold": 20})
    results = _run(pipeline)
    assert all(r.passed for r in results), [
        r.message for r in results if not r.passed
    ]


def test_missing_drift_produces_warning():
    pipeline = _FullPipeline(drift=None)
    results = _run(pipeline)
    failed = [r for r in results if not r.passed]
    assert len(failed) == 1
    assert failed[0].rule == "no-drift-config"


def test_invalid_strategy_produces_error():
    pipeline = _FullPipeline(drift={"strategy": "revert", "threshold": 10})
    results = _run(pipeline)
    failed = [r for r in results if not r.passed]
    assert any(r.rule == "invalid-drift-strategy" for r in failed)


def test_excessive_threshold_produces_warning():
    pipeline = _FullPipeline(drift={"strategy": "alert", "threshold": 999})
    results = _run(pipeline)
    failed = [r for r in results if not r.passed]
    assert any(r.rule == "drift-threshold-too-high" for r in failed)


def test_invalid_strategy_and_high_threshold_both_fail():
    pipeline = _FullPipeline(drift={"strategy": "bad", "threshold": 200})
    results = _run(pipeline)
    failed_rules = {r.rule for r in results if not r.passed}
    assert "invalid-drift-strategy" in failed_rules
    assert "drift-threshold-too-high" in failed_rules
