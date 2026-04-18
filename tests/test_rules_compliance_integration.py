import pytest
from dataclasses import dataclass
from typing import Optional
from pipecheck.rules.compliance_rules import (
    NoComplianceTagRule,
    InvalidComplianceTagRule,
    PiiWithoutOwnerRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FullPipeline:
    compliance_tag: Optional[str] = None
    owner: Optional[str] = None


_compliance_rules = [NoComplianceTagRule(), InvalidComplianceTagRule(), PiiWithoutOwnerRule()]


def _run(pipeline):
    return [r.check(pipeline) for r in _compliance_rules]


def test_valid_public_pipeline_all_pass():
    p = _FullPipeline(compliance_tag="public", owner="ops-team")
    results = _run(p)
    assert all(r.severity == Severity.OK for r in results)


def test_missing_compliance_tag_produces_warning():
    p = _FullPipeline()
    results = _run(p)
    severities = {r.rule_id: r.severity for r in results}
    assert severities["no_compliance_tag"] == Severity.WARNING


def test_invalid_compliance_tag_produces_error():
    p = _FullPipeline(compliance_tag="classified", owner="someone")
    results = _run(p)
    severities = {r.rule_id: r.severity for r in results}
    assert severities["invalid_compliance_tag"] == Severity.ERROR


def test_pii_pipeline_missing_owner_produces_error():
    p = _FullPipeline(compliance_tag="pii")
    results = _run(p)
    severities = {r.rule_id: r.severity for r in results}
    assert severities["pii_without_owner"] == Severity.ERROR
    assert severities["invalid_compliance_tag"] == Severity.OK
