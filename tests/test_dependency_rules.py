import pytest
from dataclasses import dataclass, field
from typing import List, Optional

from pipecheck.rules.base import Severity
from pipecheck.rules.dependency_rules import (
    CircularDependencyRule,
    NoDependenciesRule,
    TooManyDependenciesRule,
)


@dataclass
class _FakePipeline:
    id: Optional[str] = None
    name: Optional[str] = None
    dependencies: Optional[List[str]] = None

    def __post_init__(self):
        if self.id is None and self.name is None:
            self.id = "test_pipeline"


# --- NoDependenciesRule ---

def test_no_dependencies_returns_warning():
    p = _FakePipeline(id="my_dag", dependencies=[])
    result = NoDependenciesRule().check(p)
    assert result is not None
    assert result.severity == Severity.WARNING
    assert result.rule_id == "no-dependencies"


def test_none_dependencies_returns_warning():
    p = _FakePipeline(id="my_dag", dependencies=None)
    result = NoDependenciesRule().check(p)
    assert result is not None


def test_with_dependencies_passes_no_dep_rule():
    p = _FakePipeline(id="my_dag", dependencies=["upstream_dag"])
    result = NoDependenciesRule().check(p)
    assert result is None


# --- CircularDependencyRule ---

def test_self_dependency_returns_error():
    p = _FakePipeline(id="my_dag", dependencies=["other_dag", "my_dag"])
    result = CircularDependencyRule().check(p)
    assert result is not None
    assert result.severity == Severity.ERROR
    assert result.rule_id == "circular-dependency"
    assert "my_dag" in result.message


def test_no_self_dependency_passes():
    p = _FakePipeline(id="my_dag", dependencies=["upstream_a", "upstream_b"])
    result = CircularDependencyRule().check(p)
    assert result is None


def test_circular_uses_name_when_no_id():
    p = _FakePipeline(id=None, name="my_flow", dependencies=["my_flow"])
    result = CircularDependencyRule().check(p)
    assert result is not None
    assert "my_flow" in result.message


def test_empty_dependencies_passes_circular_rule():
    p = _FakePipeline(id="dag_x", dependencies=[])
    result = CircularDependencyRule().check(p)
    assert result is None


# --- TooManyDependenciesRule ---

def test_too_many_dependencies_returns_warning():
    deps = [f"dep_{i}" for i in range(15)]
    p = _FakePipeline(id="heavy_dag", dependencies=deps)
    result = TooManyDependenciesRule().check(p)
    assert result is not None
    assert result.severity == Severity.WARNING
    assert "15" in result.message


def test_exactly_at_limit_passes():
    deps = [f"dep_{i}" for i in range(10)]
    p = _FakePipeline(id="ok_dag", dependencies=deps)
    result = TooManyDependenciesRule().check(p)
    assert result is None


def test_custom_max_dependencies():
    deps = ["a", "b", "c"]
    p = _FakePipeline(id="small_dag", dependencies=deps)
    result = TooManyDependenciesRule(max_dependencies=2).check(p)
    assert result is not None
    assert "3" in result.message
