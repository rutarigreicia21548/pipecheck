import pytest
from dataclasses import dataclass, field
from pipecheck.rules.idempotency_rules import (
    NoIdempotencyRule,
    InvalidIdempotencyStrategyRule,
    IdempotencyWithoutKeyRule,
)


@dataclass
class _FakePipeline:
    idempotency: object = None


# --- NoIdempotencyRule ---

def test_no_idempotency_returns_warning():
    result = NoIdempotencyRule().check(_FakePipeline())
    assert not result.passed


def test_empty_string_idempotency_returns_warning():
    result = NoIdempotencyRule().check(_FakePipeline(idempotency=""))
    assert not result.passed


def test_idempotency_string_passes_no_rule():
    result = NoIdempotencyRule().check(_FakePipeline(idempotency="overwrite"))
    assert result.passed


def test_idempotency_dict_passes_no_rule():
    result = NoIdempotencyRule().check(_FakePipeline(idempotency={"strategy": "upsert", "dedup_key": "id"}))
    assert result.passed


# --- InvalidIdempotencyStrategyRule ---

def test_no_idempotency_passes_invalid_strategy_rule():
    result = InvalidIdempotencyStrategyRule().check(_FakePipeline())
    assert result.passed


@pytest.mark.parametrize("strategy", ["none", "overwrite", "skip", "upsert", "append_dedup"])
def test_valid_strategies_pass(strategy):
    result = InvalidIdempotencyStrategyRule().check(_FakePipeline(idempotency=strategy))
    assert result.passed


def test_invalid_strategy_string_returns_error():
    result = InvalidIdempotencyStrategyRule().check(_FakePipeline(idempotency="magic"))
    assert not result.passed
    assert "magic" in result.message


def test_invalid_strategy_in_dict_returns_error():
    result = InvalidIdempotencyStrategyRule().check(_FakePipeline(idempotency={"strategy": "bad", "dedup_key": "id"}))
    assert not result.passed


def test_valid_strategy_in_dict_passes():
    result = InvalidIdempotencyStrategyRule().check(_FakePipeline(idempotency={"strategy": "upsert", "dedup_key": "id"}))
    assert result.passed


# --- IdempotencyWithoutKeyRule ---

def test_no_idempotency_passes_key_rule():
    result = IdempotencyWithoutKeyRule().check(_FakePipeline())
    assert result.passed


def test_string_idempotency_passes_key_rule():
    result = IdempotencyWithoutKeyRule().check(_FakePipeline(idempotency="overwrite"))
    assert result.passed


@pytest.mark.parametrize("strategy", ["upsert", "append_dedup"])
def test_key_required_strategy_without_key_returns_error(strategy):
    result = IdempotencyWithoutKeyRule().check(_FakePipeline(idempotency={"strategy": strategy}))
    assert not result.passed
    assert "dedup_key" in result.message


@pytest.mark.parametrize("strategy", ["upsert", "append_dedup"])
def test_key_required_strategy_with_key_passes(strategy):
    result = IdempotencyWithoutKeyRule().check(_FakePipeline(idempotency={"strategy": strategy, "dedup_key": "run_id"}))
    assert result.passed


def test_overwrite_strategy_without_key_passes():
    result = IdempotencyWithoutKeyRule().check(_FakePipeline(idempotency={"strategy": "overwrite"}))
    assert result.passed
