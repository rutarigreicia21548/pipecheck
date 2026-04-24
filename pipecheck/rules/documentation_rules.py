from __future__ import annotations

import re
from dataclasses import dataclass

from pipecheck.rules.base import LintResult, Rule, Severity

_URL_RE = re.compile(r"https?://[^\s]+")
_MIN_RUNBOOK_LENGTH = 10
_MAX_CHANGELOG_ENTRIES = 20


@dataclass
class NoRunbookRule(Rule):
    name: str = "no-runbook"
    description: str = "Pipeline should have a runbook URL or path"

    def check(self, pipeline) -> LintResult:
        runbook = getattr(pipeline, "runbook", None)
        if not runbook or (isinstance(runbook, str) and not runbook.strip()):
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="No runbook defined; operators won't know how to respond to failures",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Runbook present")


@dataclass
class InvalidRunbookFormatRule(Rule):
    name: str = "invalid-runbook-format"
    description: str = "Runbook should be a valid URL or non-trivial path"

    def check(self, pipeline) -> LintResult:
        runbook = getattr(pipeline, "runbook", None)
        if not runbook or not isinstance(runbook, str):
            return LintResult(rule=self.name, severity=Severity.OK, message="No runbook to validate")
        if len(runbook.strip()) < _MIN_RUNBOOK_LENGTH:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Runbook value '{runbook}' is too short to be meaningful",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Runbook format acceptable")


@dataclass
class NoChangelogRule(Rule):
    name: str = "no-changelog"
    description: str = "Pipeline should maintain a changelog"

    def check(self, pipeline) -> LintResult:
        changelog = getattr(pipeline, "changelog", None)
        if not changelog:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="No changelog defined; consider tracking changes for auditability",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Changelog present")


@dataclass
class ChangelogTooLargeRule(Rule):
    name: str = "changelog-too-large"
    description: str = f"Changelog should not exceed {_MAX_CHANGELOG_ENTRIES} entries"

    def check(self, pipeline) -> LintResult:
        changelog = getattr(pipeline, "changelog", None)
        if not isinstance(changelog, list):
            return LintResult(rule=self.name, severity=Severity.OK, message="No list changelog to validate")
        if len(changelog) > _MAX_CHANGELOG_ENTRIES:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message=f"Changelog has {len(changelog)} entries; consider archiving old entries (max {_MAX_CHANGELOG_ENTRIES})",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Changelog size acceptable")
