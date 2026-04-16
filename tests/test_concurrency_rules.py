import pytest
from dataclasses import dataclass, field
from typing import Optional
from pipecheck.rules.concurrency_rules import (
    NoConcurrencyLimitRule,
    ConcurrencyTooHighRule,
    ZeroConcurrencyRule,
)


@dataclass
class _FakePipeline:
    concurrency: Optional[int] = None

    def __post_init__(self):
        pass


def test_no_concurrency_returns_warning():
    p = _FakePipeline(concurrency=None)
    result = NoConcurrencyLimitRule().check(p)
    assert not result.passed


def test_concurrency_present_passes_no_concurrency_rule():
    p = _FakePipeline(concurrency=4)
    result = NoConcurrencyLimitRule().check(p)
    assert result.passed


def test_concurrency_within_limit_passes():
    p = _FakePipeline(concurrency=16)
    result = ConcurrencyTooHighRule().check(p)
    assert result.passed


def test_concurrency_at_max_passes():
    p = _FakePipeline(concurrency=32)
    result = ConcurrencyTooHighRule().check(p)
    assert result.passed


def test_concurrency_exceeds_max_fails():
    p = _FakePipeline(concurrency=64)
    result = ConcurrencyTooHighRule().check(p)
    assert not result.passed
    assert "64" in result.message


def test_concurrency_too_high_custom_max():
    p = _FakePipeline(concurrency=10)
    result = ConcurrencyTooHighRule(max_concurrency=8).check(p)
    assert not result.passed


def test_concurrency_none_skips_too_high_rule():
    p = _FakePipeline(concurrency=None)
    result = ConcurrencyTooHighRule().check(p)
    assert result.passed


def test_zero_concurrency_fails():
    p = _FakePipeline(concurrency=0)
    result = ZeroConcurrencyRule().check(p)
    assert not result.passed


def test_negative_concurrency_fails():
    p = _FakePipeline(concurrency=-1)
    result = ZeroConcurrencyRule().check(p)
    assert not result.passed


def test_positive_concurrency_passes_zero_rule():
    p = _FakePipeline(concurrency=1)
    result = ZeroConcurrencyRule().check(p)
    assert result.passed


def test_none_concurrency_passes_zero_rule():
    p = _FakePipeline(concurrency=None)
    result = ZeroConcurrencyRule().check(p)
    assert result.passed
