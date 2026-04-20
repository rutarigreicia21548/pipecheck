import pytest
from dataclasses import dataclass, field
from pipecheck.rules.base import Severity
from pipecheck.rules.logging_rules import (
    NoLoggingConfigRule,
    InvalidLogLevelRule,
    LogRetentionTooLongRule,
)


@dataclass
class _FakePipeline:
    log_config: object = None


# --- NoLoggingConfigRule ---

def test_no_log_config_returns_warning():
    result = NoLoggingConfigRule().check(_FakePipeline())
    assert result.severity == Severity.WARNING


def test_empty_dict_log_config_returns_warning():
    result = NoLoggingConfigRule().check(_FakePipeline(log_config={}))
    assert result.severity == Severity.WARNING


def test_log_config_present_passes_no_logging_rule():
    result = NoLoggingConfigRule().check(_FakePipeline(log_config={"level": "INFO"}))
    assert result.severity == Severity.OK


# --- InvalidLogLevelRule ---

def test_no_log_config_passes_invalid_level_rule():
    result = InvalidLogLevelRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_non_dict_log_config_passes_invalid_level_rule():
    result = InvalidLogLevelRule().check(_FakePipeline(log_config="INFO"))
    assert result.severity == Severity.OK


def test_missing_level_key_passes_invalid_level_rule():
    result = InvalidLogLevelRule().check(_FakePipeline(log_config={"retention_days": 30}))
    assert result.severity == Severity.OK


@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
def test_valid_log_levels_pass(level):
    result = InvalidLogLevelRule().check(_FakePipeline(log_config={"level": level}))
    assert result.severity == Severity.OK


@pytest.mark.parametrize("level", ["TRACE", "VERBOSE", "info", "warn", "fatal"])
def test_invalid_log_levels_return_error(level):
    result = InvalidLogLevelRule().check(_FakePipeline(log_config={"level": level}))
    assert result.severity == Severity.ERROR
    assert level in result.message


# --- LogRetentionTooLongRule ---

def test_no_log_config_passes_retention_rule():
    result = LogRetentionTooLongRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_no_retention_days_key_passes_retention_rule():
    result = LogRetentionTooLongRule().check(_FakePipeline(log_config={"level": "INFO"}))
    assert result.severity == Severity.OK


def test_retention_within_limit_passes():
    result = LogRetentionTooLongRule().check(_FakePipeline(log_config={"retention_days": 90}))
    assert result.severity == Severity.OK


def test_retention_at_limit_passes():
    result = LogRetentionTooLongRule().check(_FakePipeline(log_config={"retention_days": 365}))
    assert result.severity == Severity.OK


def test_retention_too_long_returns_error():
    result = LogRetentionTooLongRule().check(_FakePipeline(log_config={"retention_days": 400}))
    assert result.severity == Severity.ERROR
    assert "400" in result.message


def test_non_integer_retention_returns_error():
    result = LogRetentionTooLongRule().check(_FakePipeline(log_config={"retention_days": "forever"}))
    assert result.severity == Severity.ERROR
