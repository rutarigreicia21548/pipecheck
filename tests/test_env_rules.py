import pytest
from dataclasses import dataclass, field
from typing import Optional
from pipecheck.rules.env_rules import (
    NoEnvironmentRule,
    InvalidEnvironmentRule,
    ProductionWithoutOwnerRule,
)


@dataclass
class _FakePipeline:
    pipeline_id: str = "my_pipeline"
    environment: Optional[str] = None
    owner: Optional[str] = None

    def __post_init__(self):
        pass


# --- NoEnvironmentRule ---

def test_no_environment_returns_warning():
    p = _FakePipeline(environment=None)
    result = NoEnvironmentRule().check(p)
    assert not result.passed


def test_empty_environment_returns_warning():
    p = _FakePipeline(environment="")
    result = NoEnvironmentRule().check(p)
    assert not result.passed


def test_environment_present_passes():
    p = _FakePipeline(environment="prod")
    result = NoEnvironmentRule().check(p)
    assert result.passed


# --- InvalidEnvironmentRule ---

def test_valid_environments_pass():
    for env in ["dev", "staging", "prod", "production", "development", "test"]:
        p = _FakePipeline(environment=env)
        result = InvalidEnvironmentRule().check(p)
        assert result.passed, f"Expected {env} to pass"


def test_unknown_environment_fails():
    p = _FakePipeline(environment="sandbox")
    result = InvalidEnvironmentRule().check(p)
    assert not result.passed
    assert "sandbox" in result.message


def test_none_environment_passes_invalid_env_rule():
    p = _FakePipeline(environment=None)
    result = InvalidEnvironmentRule().check(p)
    assert result.passed


def test_environment_case_insensitive():
    p = _FakePipeline(environment="PROD")
    result = InvalidEnvironmentRule().check(p)
    assert result.passed


# --- ProductionWithoutOwnerRule ---

def test_prod_without_owner_fails():
    p = _FakePipeline(environment="prod", owner=None)
    result = ProductionWithoutOwnerRule().check(p)
    assert not result.passed


def test_production_without_owner_fails():
    p = _FakePipeline(environment="production", owner=None)
    result = ProductionWithoutOwnerRule().check(p)
    assert not result.passed


def test_prod_with_owner_passes():
    p = _FakePipeline(environment="prod", owner="data-team")
    result = ProductionWithoutOwnerRule().check(p)
    assert result.passed


def test_dev_without_owner_passes():
    p = _FakePipeline(environment="dev", owner=None)
    result = ProductionWithoutOwnerRule().check(p)
    assert result.passed


def test_no_env_without_owner_passes():
    p = _FakePipeline(environment=None, owner=None)
    result = ProductionWithoutOwnerRule().check(p)
    assert result.passed
