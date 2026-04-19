import pytest
from dataclasses import dataclass, field
from pipecheck.rules.parallelism_rules import (
    NoParallelismRule,
    ParallelismTooHighRule,
    ZeroParallelismRule,
    MAX_PARALLELISM,
)
from pipecheck.rules.base import Severity


@dataclass
class _FakePipeline:
    parallelism: object = None


def test_no_parallelism_returns_warning():
    result = NoParallelismRule().check(_FakePipeline(parallelism=None))
    assert result.severity == Severity.WARNING


def test_parallelism_present_passes_no_parallelism_rule():
    result = NoParallelismRule().check(_FakePipeline(parallelism=4))
    assert result.severity == Severity.OK


def test_parallelism_within_limit_passes():
    result = ParallelismTooHighRule().check(_FakePipeline(parallelism=MAX_PARALLELISM))
    assert result.severity == Severity.OK


def test_parallelism_too_high_returns_error():
    result = ParallelismTooHighRule().check(_FakePipeline(parallelism=MAX_PARALLELISM + 1))
    assert result.severity == Severity.ERROR


def test_no_parallelism_skips_too_high_rule():
    result = ParallelismTooHighRule().check(_FakePipeline(parallelism=None))
    assert result.severity == Severity.OK


def test_zero_parallelism_returns_error():
    result = ZeroParallelismRule().check(_FakePipeline(parallelism=0))
    assert result.severity == Severity.ERROR


def test_nonzero_parallelism_passes_zero_rule():
    result = ZeroParallelismRule().check(_FakePipeline(parallelism=8))
    assert result.severity == Severity.OK


def test_none_parallelism_passes_zero_rule():
    result = ZeroParallelismRule().check(_FakePipeline(parallelism=None))
    assert result.severity == Severity.OK


def test_parallelism_one_passes_all_rules():
    p = _FakePipeline(parallelism=1)
    for rule in [NoParallelismRule(), ParallelismTooHighRule(), ZeroParallelismRule()]:
        assert rule.check(p).severity == Severity.OK
