import pytest
from dataclasses import dataclass, field
from typing import Optional
from pipecheck.rules.resource_rules import (
    NoMemoryLimitRule, MemoryLimitTooHighRule,
    NoCPULimitRule, CPULimitTooHighRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FakePipeline:
    memory_limit: Optional[int] = None
    cpu_limit: Optional[float] = None


def test_no_memory_limit_returns_warning():
    p = _FakePipeline()
    result = NoMemoryLimitRule().check(p)
    assert result.severity == Severity.WARNING


def test_memory_limit_present_passes_no_memory_rule():
    p = _FakePipeline(memory_limit=512)
    result = NoMemoryLimitRule().check(p)
    assert result.severity == Severity.OK


def test_memory_limit_within_bounds_passes():
    p = _FakePipeline(memory_limit=8192)
    result = MemoryLimitTooHighRule().check(p)
    assert result.severity == Severity.OK


def test_memory_limit_too_high_returns_error():
    p = _FakePipeline(memory_limit=32768)
    result = MemoryLimitTooHighRule().check(p)
    assert result.severity == Severity.ERROR
    assert "32768" in result.message


def test_no_memory_no_error_from_too_high_rule():
    p = _FakePipeline(memory_limit=None)
    result = MemoryLimitTooHighRule().check(p)
    assert result.severity == Severity.OK


def test_no_cpu_limit_returns_warning():
    p = _FakePipeline()
    result = NoCPULimitRule().check(p)
    assert result.severity == Severity.WARNING


def test_cpu_limit_present_passes_no_cpu_rule():
    p = _FakePipeline(cpu_limit=4)
    result = NoCPULimitRule().check(p)
    assert result.severity == Severity.OK


def test_cpu_limit_within_bounds_passes():
    p = _FakePipeline(cpu_limit=8)
    result = CPULimitTooHighRule().check(p)
    assert result.severity == Severity.OK


def test_cpu_limit_too_high_returns_error():
    p = _FakePipeline(cpu_limit=64)
    result = CPULimitTooHighRule().check(p)
    assert result.severity == Severity.ERROR
    assert "64" in result.message


def test_no_cpu_no_error_from_too_high_rule():
    p = _FakePipeline(cpu_limit=None)
    result = CPULimitTooHighRule().check(p)
    assert result.severity == Severity.OK


@pytest.mark.parametrize("memory_limit,expected_severity", [
    (None, Severity.WARNING),
    (0, Severity.WARNING),
    (1, Severity.OK),
    (512, Severity.OK),
])
def test_no_memory_limit_rule_parametrized(memory_limit, expected_severity):
    """Verify NoMemoryLimitRule across boundary and typical values."""
    p = _FakePipeline(memory_limit=memory_limit)
    result = NoMemoryLimitRule().check(p)
    assert result.severity == expected_severity
