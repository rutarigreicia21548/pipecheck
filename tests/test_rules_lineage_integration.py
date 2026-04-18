import pytest
from dataclasses import dataclass, field
from typing import Any, Optional
from pipecheck.rules import run_rules
from pipecheck.rules.lineage_rules import (
    NoLineageRule,
    MissingLineageInputsRule,
    MissingLineageOutputsRule,
    InvalidLineageDatasetRule,
)


@dataclass
class _FullPipeline:
    dag_id: str = "my_pipeline"
    schedule: str = "@daily"
    tags: list = field(default_factory=lambda: ["team:data"])
    lineage: Any = None

    def __post_init__(self):
        if self.lineage is None:
            self.lineage = {"inputs": ["s3://raw/data"], "outputs": ["warehouse.processed"]}


def _lineage_rules():
    return [
        NoLineageRule(),
        MissingLineageInputsRule(),
        MissingLineageOutputsRule(),
        InvalidLineageDatasetRule(),
    ]


def test_valid_lineage_all_pass():
    pipeline = _FullPipeline()
    results = run_rules(pipeline, rules=_lineage_rules())
    assert all(r.passed for r in results)


def test_missing_lineage_produces_warnings():
    pipeline = _FullPipeline(lineage={})
    results = run_rules(pipeline, rules=_lineage_rules())
    failed = [r for r in results if not r.passed]
    assert any(r.rule_id == "no-lineage" for r in failed)


def test_invalid_dataset_produces_error():
    pipeline = _FullPipeline(lineage={"inputs": [""], "outputs": ["warehouse.out"]})
    results = run_rules(pipeline, rules=_lineage_rules())
    failed = [r for r in results if not r.passed]
    assert any(r.rule_id == "invalid-lineage-dataset" for r in failed)
