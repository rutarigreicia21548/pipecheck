import pytest
from dataclasses import dataclass, field
from typing import Any, Optional
from pipecheck.rules.lineage_rules import (
    NoLineageRule,
    MissingLineageInputsRule,
    MissingLineageOutputsRule,
    InvalidLineageDatasetRule,
)


@dataclass
class _FakePipeline:
    lineage: Any = None


def test_no_lineage_returns_warning():
    result = NoLineageRule().check(_FakePipeline(lineage=None))
    assert not result.passed


def test_empty_dict_lineage_returns_warning():
    result = NoLineageRule().check(_FakePipeline(lineage={}))
    assert not result.passed


def test_lineage_present_passes_no_lineage_rule():
    result = NoLineageRule().check(_FakePipeline(lineage={"inputs": ["s3://bucket/in"], "outputs": ["s3://bucket/out"]}))
    assert result.passed


def test_missing_inputs_returns_warning():
    result = MissingLineageInputsRule().check(_FakePipeline(lineage={"outputs": ["s3://bucket/out"]}))
    assert not result.passed


def test_empty_inputs_returns_warning():
    result = MissingLineageInputsRule().check(_FakePipeline(lineage={"inputs": [], "outputs": ["s3://bucket/out"]}))
    assert not result.passed


def test_inputs_present_passes():
    result = MissingLineageInputsRule().check(_FakePipeline(lineage={"inputs": ["db.table"], "outputs": []}))
    assert result.passed


def test_missing_outputs_returns_warning():
    result = MissingLineageOutputsRule().check(_FakePipeline(lineage={"inputs": ["db.table"]}))
    assert not result.passed


def test_empty_outputs_returns_warning():
    result = MissingLineageOutputsRule().check(_FakePipeline(lineage={"inputs": ["db.table"], "outputs": []}))
    assert not result.passed


def test_outputs_present_passes():
    result = MissingLineageOutputsRule().check(_FakePipeline(lineage={"inputs": [], "outputs": ["warehouse.table"]}))
    assert result.passed


def test_invalid_dataset_empty_string_returns_error():
    result = InvalidLineageDatasetRule().check(
        _FakePipeline(lineage={"inputs": [""], "outputs": ["warehouse.table"]})
    )
    assert not result.passed


def test_invalid_dataset_non_string_returns_error():
    result = InvalidLineageDatasetRule().check(
        _FakePipeline(lineage={"inputs": [123], "outputs": ["warehouse.table"]})
    )
    assert not result.passed


def test_valid_datasets_pass():
    result = InvalidLineageDatasetRule().check(
        _FakePipeline(lineage={"inputs": ["s3://in"], "outputs": ["s3://out"]})
    )
    assert result.passed


def test_no_lineage_skips_dataset_check():
    result = InvalidLineageDatasetRule().check(_FakePipeline(lineage=None))
    assert result.passed
