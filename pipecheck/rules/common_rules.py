"""Common lint rules applicable to both Airflow and Prefect pipelines."""
from __future__ import annotations

import re
from typing import Any

from pipecheck.rules.base import Rule, LintResult, Severity

_VALID_ID_RE = re.compile(r'^[a-zA-Z0-9_\-\.]+$')


class NoPipelineIdRule(Rule):
    """Ensure every pipeline has a non-empty identifier."""

    rule_id = "PC001"
    severity = Severity.ERROR
    description = "Pipeline must have a non-empty id/name."

    def check(self, pipeline: Any) -> list[LintResult]:
        pid = getattr(pipeline, "dag_id", None) or getattr(pipeline, "name", None)
        if not pid:
            return [self._result("<unknown>", "Pipeline is missing a required id or name.")]
        return []


class InvalidIdCharactersRule(Rule):
    """Warn when a pipeline id contains characters that may cause issues."""

    rule_id = "PC002"
    severity = Severity.WARNING
    description = "Pipeline id should only contain alphanumerics, underscores, hyphens, or dots."

    def check(self, pipeline: Any) -> list[LintResult]:
        pid = getattr(pipeline, "dag_id", None) or getattr(pipeline, "name", None) or ""
        if pid and not _VALID_ID_RE.match(pid):
            return [
                self._result(
                    pid,
                    f"Pipeline id '{pid}' contains invalid characters.",
                    pattern=_VALID_ID_RE.pattern,
                )
            ]
        return []


class NoTagsRule(Rule):
    """Inform when a pipeline has no tags defined."""

    rule_id = "PC003"
    severity = Severity.INFO
    description = "Pipeline should define at least one tag for discoverability."

    def check(self, pipeline: Any) -> list[LintResult]:
        pid = getattr(pipeline, "dag_id", None) or getattr(pipeline, "name", None) or "<unknown>"
        tags = getattr(pipeline, "tags", None) or []
        if not tags:
            return [self._result(pid, "Pipeline has no tags defined.")]
        return []


DEFAULT_RULES: list[Rule] = [
    NoPipelineIdRule(),
    InvalidIdCharactersRule(),
    NoTagsRule(),
]
