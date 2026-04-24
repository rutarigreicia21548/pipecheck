from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

import pytest

from pipecheck.rules.base import Severity
from pipecheck.rules.documentation_rules import (
    ChangelogTooLargeRule,
    NoChangelogRule,
    NoRunbookRule,
    InvalidRunbookFormatRule,
)


@dataclass
class _FakePipeline:
    runbook: Optional[Any] = None
    changelog: Optional[Any] = None


# --- NoRunbookRule ---

def test_no_runbook_returns_warning():
    result = NoRunbookRule().check(_FakePipeline())
    assert result.severity == Severity.WARNING


def test_empty_string_runbook_returns_warning():
    result = NoRunbookRule().check(_FakePipeline(runbook="   "))
    assert result.severity == Severity.WARNING


def test_runbook_present_passes_no_runbook_rule():
    result = NoRunbookRule().check(_FakePipeline(runbook="https://wiki.example.com/runbook"))
    assert result.severity == Severity.OK


# --- InvalidRunbookFormatRule ---

def test_no_runbook_passes_invalid_format_rule():
    result = InvalidRunbookFormatRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_short_runbook_returns_error():
    result = InvalidRunbookFormatRule().check(_FakePipeline(runbook="run"))
    assert result.severity == Severity.ERROR


def test_long_enough_runbook_passes_format_rule():
    result = InvalidRunbookFormatRule().check(_FakePipeline(runbook="https://wiki.example.com/runbook/my-pipeline"))
    assert result.severity == Severity.OK


def test_exactly_min_length_runbook_passes():
    # 10 characters — exactly at the boundary
    result = InvalidRunbookFormatRule().check(_FakePipeline(runbook="a" * 10))
    assert result.severity == Severity.OK


def test_one_below_min_length_returns_error():
    result = InvalidRunbookFormatRule().check(_FakePipeline(runbook="a" * 9))
    assert result.severity == Severity.ERROR


# --- NoChangelogRule ---

def test_no_changelog_returns_warning():
    result = NoChangelogRule().check(_FakePipeline())
    assert result.severity == Severity.WARNING


def test_empty_list_changelog_returns_warning():
    # Empty list is falsy
    result = NoChangelogRule().check(_FakePipeline(changelog=[]))
    assert result.severity == Severity.WARNING


def test_changelog_present_passes_no_changelog_rule():
    result = NoChangelogRule().check(_FakePipeline(changelog=["v1.0 - initial release"]))
    assert result.severity == Severity.OK


def test_changelog_string_passes_no_changelog_rule():
    result = NoChangelogRule().check(_FakePipeline(changelog="See CHANGELOG.md"))
    assert result.severity == Severity.OK


# --- ChangelogTooLargeRule ---

def test_no_changelog_passes_too_large_rule():
    result = ChangelogTooLargeRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_small_changelog_passes_too_large_rule():
    result = ChangelogTooLargeRule().check(_FakePipeline(changelog=["entry"] * 5))
    assert result.severity == Severity.OK


def test_exactly_max_changelog_passes():
    result = ChangelogTooLargeRule().check(_FakePipeline(changelog=["entry"] * 20))
    assert result.severity == Severity.OK


def test_oversized_changelog_returns_warning():
    result = ChangelogTooLargeRule().check(_FakePipeline(changelog=["entry"] * 21))
    assert result.severity == Severity.WARNING


def test_string_changelog_passes_too_large_rule():
    # Non-list changelogs are not validated for size
    result = ChangelogTooLargeRule().check(_FakePipeline(changelog="See CHANGELOG.md"))
    assert result.severity == Severity.OK
