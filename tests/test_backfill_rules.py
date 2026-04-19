import pytest
from dataclasses import dataclass, field
from typing import Optional
from pipecheck.rules.backfill_rules import (
    NoBackfillConfigRule,
    InvalidBackfillStrategyRule,
    BackfillWindowTooLargeRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FakePipeline:
    backfill: Optional[object] = None


def test_no_backfill_returns_warning():
    p = _FakePipeline(backfill=None)
    result = NoBackfillConfigRule().check(p)
    assert result.severity == Severity.WARNING


def test_empty_dict_backfill_returns_warning():
    p = _FakePipeline(backfill={})
    result = NoBackfillConfigRule().check(p)
    assert result.severity == Severity.WARNING


def test_backfill_present_passes_no_backfill_rule():
    p = _FakePipeline(backfill={"strategy": "incremental"})
    result = NoBackfillConfigRule().check(p)
    assert result.severity == Severity.OK


def test_valid_strategy_passes_invalid_rule():
    for strategy in ("full", "incremental", "none"):
        p = _FakePipeline(backfill={"strategy": strategy})
        result = InvalidBackfillStrategyRule().check(p)
        assert result.severity == Severity.OK


def test_invalid_strategy_returns_error():
    p = _FakePipeline(backfill={"strategy": "partial"})
    result = InvalidBackfillStrategyRule().check(p)
    assert result.severity == Severity.ERROR
    assert "partial" in result.message


def test_no_strategy_key_passes_invalid_rule():
    p = _FakePipeline(backfill={"window_days": 30})
    result = InvalidBackfillStrategyRule().check(p)
    assert result.severity == Severity.OK


def test_non_dict_backfill_passes_invalid_strategy_rule():
    p = _FakePipeline(backfill="incremental")
    result = InvalidBackfillStrategyRule().check(p)
    assert result.severity == Severity.OK


def test_window_within_limit_passes():
    p = _FakePipeline(backfill={"window_days": 90})
    result = BackfillWindowTooLargeRule().check(p)
    assert result.severity == Severity.OK


def test_window_too_large_returns_warning():
    p = _FakePipeline(backfill={"window_days": 400})
    result = BackfillWindowTooLargeRule().check(p)
    assert result.severity == Severity.WARNING
    assert "400" in result.message


def test_no_window_key_passes_window_rule():
    p = _FakePipeline(backfill={"strategy": "full"})
    result = BackfillWindowTooLargeRule().check(p)
    assert result.severity == Severity.OK


def test_no_backfill_passes_window_rule():
    p = _FakePipeline(backfill=None)
    result = BackfillWindowTooLargeRule().check(p)
    assert result.severity == Severity.OK
