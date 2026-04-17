import pytest
from dataclasses import dataclass
from pipecheck.rules import run_rules
from pipecheck.rules.metadata_rules import (
    NoMetadataRule,
    InvalidMetadataTypeRule,
    EmptyMetadataRule,
    ReservedMetadataKeyRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FullPipeline:
    pipeline_id: str = "my_pipeline"
    name: str = "My Pipeline"
    metadata: object = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {"team": "data-eng", "cost_center": "cc-99"}


METADATA_RULES = [
    NoMetadataRule(),
    InvalidMetadataTypeRule(),
    EmptyMetadataRule(),
    ReservedMetadataKeyRule(),
]


def test_valid_metadata_all_pass():
    pipeline = _FullPipeline()
    results = run_rules(pipeline, rules=METADATA_RULES)
    assert all(r.severity == Severity.OK for r in results)


def test_missing_metadata_produces_warning():
    pipeline = _FullPipeline(metadata=None)
    # override post_init side effect
    pipeline.metadata = None
    results = run_rules(pipeline, rules=METADATA_RULES)
    warnings = [r for r in results if r.severity == Severity.WARNING]
    assert any(r.rule_id == "no-metadata" for r in warnings)


def test_reserved_key_produces_error():
    pipeline = _FullPipeline()
    pipeline.metadata = {"id": "overriding", "team": "data"}
    results = run_rules(pipeline, rules=METADATA_RULES)
    errors = [r for r in results if r.severity == Severity.ERROR]
    assert any(r.rule_id == "reserved-metadata-key" for r in errors)


def test_empty_metadata_produces_warning():
    pipeline = _FullPipeline()
    pipeline.metadata = {}
    results = run_rules(pipeline, rules=METADATA_RULES)
    warnings = [r for r in results if r.severity == Severity.WARNING]
    assert any(r.rule_id == "empty-metadata" for r in warnings)
