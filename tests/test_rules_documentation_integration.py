from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

from pipecheck.rules.base import Severity
from pipecheck.rules.documentation_rules import (
    ChangelogTooLargeRule,
    InvalidRunbookFormatRule,
    NoChangelogRule,
    NoRunbookRule,
)


@dataclass
class _FullPipeline:
    runbook: Optional[Any] = None
    changelog: Optional[Any] = None


def _doc_rules():
    return [
        NoRunbookRule(),
        InvalidRunbookFormatRule(),
        NoChangelogRule(),
        ChangelogTooLargeRule(),
    ]


def _check_all(pipeline):
    return [rule.check(pipeline) for rule in _doc_rules()]


def test_valid_documentation_all_pass():
    pipeline = _FullPipeline(
        runbook="https://wiki.example.com/runbooks/my-pipeline",
        changelog=["v1.1 - added retry logic", "v1.0 - initial release"],
    )
    results = _check_all(pipeline)
    assert all(r.severity == Severity.OK for r in results), [
        str(r) for r in results if r.severity != Severity.OK
    ]


def test_missing_runbook_and_changelog_produces_warnings():
    pipeline = _FullPipeline()
    results = _check_all(pipeline)
    severities = {r.rule: r.severity for r in results}
    assert severities["no-runbook"] == Severity.WARNING
    assert severities["no-changelog"] == Severity.WARNING
    # Format rules pass when fields are absent
    assert severities["invalid-runbook-format"] == Severity.OK
    assert severities["changelog-too-large"] == Severity.OK


def test_short_runbook_produces_error():
    pipeline = _FullPipeline(runbook="fix", changelog=["v1.0"])
    results = _check_all(pipeline)
    severities = {r.rule: r.severity for r in results}
    assert severities["invalid-runbook-format"] == Severity.ERROR
    # runbook is present so no-runbook passes
    assert severities["no-runbook"] == Severity.OK


def test_oversized_changelog_produces_warning():
    pipeline = _FullPipeline(
        runbook="https://wiki.example.com/runbooks/my-pipeline",
        changelog=[f"v{i}.0" for i in range(25)],
    )
    results = _check_all(pipeline)
    severities = {r.rule: r.severity for r in results}
    assert severities["changelog-too-large"] == Severity.WARNING
    assert severities["no-changelog"] == Severity.OK
