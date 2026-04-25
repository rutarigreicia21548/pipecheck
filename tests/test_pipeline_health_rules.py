from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import pytest

from pipecheck.rules.pipeline_health_rules import (
    InvalidHealthStatusRule,
    NoPipelineHealthRule,
    TerminalHealthWithoutDeprecationRule,
)


@dataclass
class _FakePipeline:
    health: Optional[str] = None
    deprecation_policy: Optional[Any] = None


# --- NoPipelineHealthRule ---

def test_no_health_returns_warning():
    result = NoPipelineHealthRule().check(_FakePipeline())
    assert not result.passed
    assert "health" in result.message.lower()


def test_empty_string_health_returns_warning():
    result = NoPipelineHealthRule().check(_FakePipeline(health=""))
    assert not result.passed


def test_health_present_passes_no_health_rule():
    result = NoPipelineHealthRule().check(_FakePipeline(health="active"))
    assert result.passed


# --- InvalidHealthStatusRule ---

@pytest.mark.parametrize("status", ["active", "healthy", "running", "degraded", "unstable", "flapping", "disabled", "archived", "deprecated", "failed"])
def test_valid_health_statuses_pass(status):
    result = InvalidHealthStatusRule().check(_FakePipeline(health=status))
    assert result.passed


def test_unknown_health_status_returns_error():
    result = InvalidHealthStatusRule().check(_FakePipeline(health="zombie"))
    assert not result.passed
    assert "zombie" in result.message


def test_no_health_passes_invalid_status_rule():
    result = InvalidHealthStatusRule().check(_FakePipeline())
    assert result.passed


def test_health_status_case_insensitive():
    result = InvalidHealthStatusRule().check(_FakePipeline(health="ACTIVE"))
    assert result.passed


# --- TerminalHealthWithoutDeprecationRule ---

@pytest.mark.parametrize("status", ["disabled", "archived", "deprecated", "failed"])
def test_terminal_status_without_deprecation_returns_warning(status):
    result = TerminalHealthWithoutDeprecationRule().check(_FakePipeline(health=status))
    assert not result.passed
    assert "deprecation_policy" in result.message


@pytest.mark.parametrize("status", ["disabled", "archived", "deprecated", "failed"])
def test_terminal_status_with_deprecation_passes(status):
    pipeline = _FakePipeline(health=status, deprecation_policy={"date": "2025-12-31"})
    result = TerminalHealthWithoutDeprecationRule().check(pipeline)
    assert result.passed


def test_active_status_without_deprecation_passes():
    result = TerminalHealthWithoutDeprecationRule().check(_FakePipeline(health="active"))
    assert result.passed


def test_no_health_passes_terminal_rule():
    result = TerminalHealthWithoutDeprecationRule().check(_FakePipeline())
    assert result.passed
