import pytest
from dataclasses import dataclass
from pipecheck.rules.deprecation_rules import (
    NoDeprecationPolicyRule,
    InvalidDeprecationDateRule,
    DeprecatedPipelineActiveRule,
    NoDeprecationOwnerRule,
)
from pipecheck.rules.base import Severity


@dataclass
class _FullPipeline:
    deprecation_policy: object = None
    active: bool = True


def _deprecation_rules():
    return [
        NoDeprecationPolicyRule(),
        InvalidDeprecationDateRule(),
        DeprecatedPipelineActiveRule(),
        NoDeprecationOwnerRule(),
    ]


def test_valid_deprecation_all_pass():
    pipeline = _FullPipeline(
        deprecation_policy={"deprecate_on": "2099-01-01", "owner": "platform-team"},
        active=True,
    )
    results = [r.check(pipeline) for r in _deprecation_rules()]
    assert all(r.severity == Severity.OK for r in results)


def test_missing_deprecation_policy_produces_warning():
    pipeline = _FullPipeline(deprecation_policy=None)
    results = [r.check(pipeline) for r in _deprecation_rules()]
    severities = {r.rule: r.severity for r in results}
    assert severities["no_deprecation_policy"] == Severity.WARNING
    # other rules skip gracefully
    assert severities["invalid_deprecation_date"] == Severity.OK
    assert severities["deprecated_pipeline_active"] == Severity.OK
    assert severities["no_deprecation_owner"] == Severity.OK


def test_past_date_and_active_produces_error():
    pipeline = _FullPipeline(
        deprecation_policy={"deprecate_on": "2001-06-01", "owner": "team"},
        active=True,
    )
    results = {r.rule: r for r in [rule.check(pipeline) for rule in _deprecation_rules()]}
    assert results["deprecated_pipeline_active"].severity == Severity.ERROR


def test_invalid_date_format_produces_error():
    pipeline = _FullPipeline(
        deprecation_policy={"deprecate_on": "01/01/2030", "owner": "team"},
        active=True,
    )
    results = {r.rule: r for r in [rule.check(pipeline) for rule in _deprecation_rules()]}
    assert results["invalid_deprecation_date"].severity == Severity.ERROR
