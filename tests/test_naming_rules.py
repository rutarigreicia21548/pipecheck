"""Tests for naming convention rules."""

import pytest
from dataclasses import dataclass, field
from typing import List, Optional

from pipecheck.rules.naming_rules import IdTooLongRule, SnakeCaseIdRule, TagNamingRule
from pipecheck.rules.base import Severity


@dataclass
class _FakePipeline:
    dag_id: Optional[str] = None
    name: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        # Ensure only one id field is set at a time for clarity
        if self.dag_id and self.name:
            raise ValueError("Set only dag_id or name, not both")


# --- SnakeCaseIdRule ---

def test_snake_case_passes():
    rule = SnakeCaseIdRule()
    assert rule.check(_FakePipeline(dag_id="my_pipeline_01")) is None


def test_camel_case_fails():
    rule = SnakeCaseIdRule()
    result = rule.check(_FakePipeline(dag_id="MyPipeline"))
    assert result is not None
    assert result.severity == Severity.WARNING
    assert "MyPipeline" in result.message


def test_id_with_spaces_fails():
    rule = SnakeCaseIdRule()
    result = rule.check(_FakePipeline(name="my pipeline"))
    assert result is not None
    assert "my pipeline" in result.message


def test_id_with_hyphens_fails():
    rule = SnakeCaseIdRule()
    result = rule.check(_FakePipeline(dag_id="my-pipeline"))
    assert result is not None


def test_no_id_returns_none_snake_case():
    rule = SnakeCaseIdRule()
    assert rule.check(_FakePipeline()) is None


# --- IdTooLongRule ---

def test_short_id_passes():
    rule = IdTooLongRule()
    assert rule.check(_FakePipeline(dag_id="short_id")) is None


def test_exactly_max_length_passes():
    rule = IdTooLongRule()
    pid = "a" * IdTooLongRule.MAX_LENGTH
    assert rule.check(_FakePipeline(dag_id=pid)) is None


def test_over_max_length_fails():
    rule = IdTooLongRule()
    pid = "a" * (IdTooLongRule.MAX_LENGTH + 1)
    result = rule.check(_FakePipeline(dag_id=pid))
    assert result is not None
    assert result.severity == Severity.WARNING
    assert str(IdTooLongRule.MAX_LENGTH) in result.message


def test_no_id_returns_none_too_long():
    rule = IdTooLongRule()
    assert rule.check(_FakePipeline()) is None


# --- TagNamingRule ---

def test_valid_tags_pass():
    rule = TagNamingRule()
    assert rule.check(_FakePipeline(dag_id="x", tags=["team-a", "v1.0", "prod"])) is None


def test_tag_with_uppercase_fails():
    rule = TagNamingRule()
    result = rule.check(_FakePipeline(dag_id="x", tags=["Team-A"]))
    assert result is not None
    assert "Team-A" in result.message


def test_tag_with_space_fails():
    rule = TagNamingRule()
    result = rule.check(_FakePipeline(dag_id="x", tags=["my tag"]))
    assert result is not None


def test_empty_tags_passes():
    rule = TagNamingRule()
    assert rule.check(_FakePipeline(dag_id="x", tags=[])) is None


def test_mixed_valid_invalid_tags_fails():
    rule = TagNamingRule()
    result = rule.check(_FakePipeline(dag_id="x", tags=["good-tag", "Bad Tag"]))
    assert result is not None
    assert "Bad Tag" in result.message
