"""Naming convention rules for pipeline IDs and tags."""

import re
from dataclasses import dataclass
from typing import Optional

from pipecheck.rules.base import LintResult, Rule, Severity


class SnakeCaseIdRule(Rule):
    """Pipeline ID should use snake_case naming convention."""

    id = "snake-case-id"
    description = "Pipeline ID should use snake_case (lowercase letters, digits, underscores)"
    severity = Severity.WARNING

    _SNAKE_CASE_RE = re.compile(r'^[a-z][a-z0-9_]*$')

    def check(self, pipeline) -> Optional[LintResult]:
        pid = getattr(pipeline, "dag_id", None) or getattr(pipeline, "name", None)
        if not pid:
            return None
        if not self._SNAKE_CASE_RE.match(pid):
            return LintResult(
                rule_id=self.id,
                severity=self.severity,
                message=(
                    f"Pipeline ID '{pid}' does not follow snake_case convention. "
                    "Use lowercase letters, digits, and underscores only."
                ),
            )
        return None


class IdTooLongRule(Rule):
    """Pipeline ID should not exceed a maximum length."""

    id = "id-too-long"
    description = "Pipeline ID should not exceed 64 characters"
    severity = Severity.WARNING
    MAX_LENGTH = 64

    def check(self, pipeline) -> Optional[LintResult]:
        pid = getattr(pipeline, "dag_id", None) or getattr(pipeline, "name", None)
        if not pid:
            return None
        if len(pid) > self.MAX_LENGTH:
            return LintResult(
                rule_id=self.id,
                severity=self.severity,
                message=(
                    f"Pipeline ID '{pid}' is {len(pid)} characters long; "
                    f"maximum recommended length is {self.MAX_LENGTH}."
                ),
            )
        return None


class TagNamingRule(Rule):
    """Tags should be lowercase and contain no spaces."""

    id = "tag-naming"
    description = "Tags should be lowercase and contain no whitespace"
    severity = Severity.WARNING

    _VALID_TAG_RE = re.compile(r'^[a-z0-9][a-z0-9_.\-]*$')

    def check(self, pipeline) -> Optional[LintResult]:
        tags = getattr(pipeline, "tags", None) or []
        bad_tags = [t for t in tags if not self._VALID_TAG_RE.match(t)]
        if bad_tags:
            return LintResult(
                rule_id=self.id,
                severity=self.severity,
                message=(
                    f"Tag(s) {bad_tags} do not follow naming convention. "
                    "Tags must be lowercase, start with a letter or digit, "
                    "and contain only letters, digits, dots, hyphens, or underscores."
                ),
            )
        return None
