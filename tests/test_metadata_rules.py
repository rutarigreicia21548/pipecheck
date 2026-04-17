import pytest
from dataclasses import dataclass, field
from typing import Any
from pipecheck.rules.metadata_rules import (
    NoMetadataRule,
    InvalidMetadataTypeRule,
    EmptyMetadataRule,
    ReservedMetadataKeyRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FakePipeline:
    metadata: Any = None


def test_no_metadata_returns_warning():
    result = NoMetadataRule().check(_FakePipeline(metadata=None))
    assert result.severity == Severity.WARNING


def test_metadata_present_passes_no_metadata_rule():
    result = NoMetadataRule().check(_FakePipeline(metadata={"team": "data"}))
    assert result.severity == Severity.OK


def test_invalid_metadata_type_string_returns_error():
    result = InvalidMetadataTypeRule().check(_FakePipeline(metadata="bad"))
    assert result.severity == Severity.ERROR
    assert "dict" in result.message


def test_invalid_metadata_type_list_returns_error():
    result = InvalidMetadataTypeRule().check(_FakePipeline(metadata=["a"]))
    assert result.severity == Severity.ERROR


def test_valid_metadata_type_passes():
    result = InvalidMetadataTypeRule().check(_FakePipeline(metadata={"k": "v"}))
    assert result.severity == Severity.OK


def test_none_metadata_skips_type_check():
    result = InvalidMetadataTypeRule().check(_FakePipeline(metadata=None))
    assert result.severity == Severity.OK


def test_empty_metadata_returns_warning():
    result = EmptyMetadataRule().check(_FakePipeline(metadata={}))
    assert result.severity == Severity.WARNING


def test_non_empty_metadata_passes_empty_rule():
    result = EmptyMetadataRule().check(_FakePipeline(metadata={"env": "prod"}))
    assert result.severity == Severity.OK


def test_reserved_key_id_returns_error():
    result = ReservedMetadataKeyRule().check(_FakePipeline(metadata={"id": "x"}))
    assert result.severity == Severity.ERROR
    assert "id" in result.message


def test_reserved_key_name_returns_error():
    result = ReservedMetadataKeyRule().check(_FakePipeline(metadata={"name": "x"}))
    assert result.severity == Severity.ERROR


def test_reserved_key_version_returns_error():
    result = ReservedMetadataKeyRule().check(_FakePipeline(metadata={"version": "1"}))
    assert result.severity == Severity.ERROR


def test_safe_metadata_keys_pass():
    result = ReservedMetadataKeyRule().check(_FakePipeline(metadata={"team": "eng", "cost_center": "42"}))
    assert result.severity == Severity.OK


def test_reserved_key_rule_skips_non_dict():
    result = ReservedMetadataKeyRule().check(_FakePipeline(metadata=None))
    assert result.severity == Severity.OK
