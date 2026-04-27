from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pipecheck.rules.quota_rules import (
    InvalidQuotaUnitRule,
    NoQuotaConfigRule,
    QuotaLimitTooHighRule,
)


@dataclass
class _FullPipeline:
    """Minimal pipeline with all fields the quota rules inspect."""
    quota: Any = None


def _quota_rules():
    return [NoQuotaConfigRule(), InvalidQuotaUnitRule(), QuotaLimitTooHighRule()]


def _run(pipeline):
    return [rule.check(pipeline) for rule in _quota_rules()]


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------

def test_valid_quota_all_pass():
    pipeline = _FullPipeline(quota={"limit": 5_000, "unit": "requests/hour"})
    results = _run(pipeline)
    assert all(r.passed for r in results), [r for r in results if not r.passed]


def test_missing_quota_produces_warning():
    pipeline = _FullPipeline()
    results = _run(pipeline)
    failed = [r for r in results if not r.passed]
    assert len(failed) == 1
    assert failed[0].rule == "no-quota-config"


def test_invalid_unit_produces_error():
    pipeline = _FullPipeline(quota={"limit": 100, "unit": "per_tick"})
    results = _run(pipeline)
    failed = [r for r in results if not r.passed]
    assert any(r.rule == "invalid-quota-unit" for r in failed)


def test_excessive_limit_produces_warning():
    pipeline = _FullPipeline(quota={"limit": 999_999, "unit": "requests/day"})
    results = _run(pipeline)
    failed = [r for r in results if not r.passed]
    assert any(r.rule == "quota-limit-too-high" for r in failed)


def test_invalid_unit_and_excessive_limit_both_fail():
    pipeline = _FullPipeline(quota={"limit": 500_000, "unit": "badunit"})
    results = _run(pipeline)
    failed_rules = {r.rule for r in results if not r.passed}
    assert "invalid-quota-unit" in failed_rules
    assert "quota-limit-too-high" in failed_rules
