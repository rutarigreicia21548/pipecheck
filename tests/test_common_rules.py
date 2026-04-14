"""Tests for common lint rules."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pytest

from pipecheck.rules.base import Severity
from pipecheck.rules.common_rules import (
    NoPipelineIdRule,
    InvalidIdCharactersRule,
    NoTagsRule,
    DEFAULT_RULES,
)


@dataclass
class _FakePipeline:
    dag_id: Optional[str] = None
    name: Optional[str] = None
    tags: list[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


# --- NoPipelineIdRule ---

def test_no_id_returns_error():
    rule = NoPipelineIdRule()
    results = rule.check(_FakePipeline())
    assert len(results) == 1
    assert results[0].severity == Severity.ERROR
    assert results[0].rule_id == "PC001"


def test_dag_id_present_passes():
    rule = NoPipelineIdRule()
    assert rule.check(_FakePipeline(dag_id="my_dag")) == []


def test_name_present_passes():
    rule = NoPipelineIdRule()
    assert rule.check(_FakePipeline(name="my_flow")) == []


# --- InvalidIdCharactersRule ---

@pytest.mark.parametrize("pid", ["valid_id", "my-dag.v2", "Pipeline123"])
def test_valid_ids_pass(pid):
    rule = InvalidIdCharactersRule()
    assert rule.check(_FakePipeline(dag_id=pid)) == []


@pytest.mark.parametrize("pid", ["my dag", "dag@v1", "flow/test"])
def test_invalid_ids_warn(pid):
    rule = InvalidIdCharactersRule()
    results = rule.check(_FakePipeline(dag_id=pid))
    assert len(results) == 1
    assert results[0].severity == Severity.WARNING
    assert results[0].rule_id == "PC002"


# --- NoTagsRule ---

def test_no_tags_returns_info():
    rule = NoTagsRule()
    results = rule.check(_FakePipeline(dag_id="my_dag", tags=[]))
    assert len(results) == 1
    assert results[0].severity == Severity.INFO
    assert results[0].rule_id == "PC003"


def test_with_tags_passes():
    rule = NoTagsRule()
    assert rule.check(_FakePipeline(dag_id="my_dag", tags=["team-a"])) == []


# --- DEFAULT_RULES ---

def test_default_rules_contains_all_rules():
    rule_ids = {r.rule_id for r in DEFAULT_RULES}
    assert {"PC001", "PC002", "PC003"}.issubset(rule_ids)
