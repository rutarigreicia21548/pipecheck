"""Lint rules package for pipecheck.

Exposes a default rule registry used by the CLI linter.
"""

from __future__ import annotations

from pipecheck.rules.base import LintResult, Rule, Severity
from pipecheck.rules.common_rules import (
    InvalidIdCharactersRule,
    NoPipelineIdRule,
    NoTagsRule,
)
from pipecheck.rules.schedule_rules import (
    FrequentScheduleRule,
    InvalidCronScheduleRule,
    NoScheduleRule,
)

__all__ = [
    # base
    "LintResult",
    "Rule",
    "Severity",
    # common
    "NoPipelineIdRule",
    "InvalidIdCharactersRule",
    "NoTagsRule",
    # schedule
    "NoScheduleRule",
    "InvalidCronScheduleRule",
    "FrequentScheduleRule",
]

#: Default ordered list of rules applied during a lint run.
DEFAULT_RULES: list[Rule] = [
    NoPipelineIdRule(),
    InvalidIdCharactersRule(),
    NoTagsRule(),
    NoScheduleRule(),
    InvalidCronScheduleRule(),
    FrequentScheduleRule(),
]


def run_rules(pipeline: object, rules: list[Rule] | None = None) -> list[LintResult]:
    """Run *rules* (default: :data:`DEFAULT_RULES`) against *pipeline*.

    Returns a list of :class:`LintResult` objects for every failed check.
    """
    active_rules = rules if rules is not None else DEFAULT_RULES
    results: list[LintResult] = []
    for rule in active_rules:
        result = rule.check(pipeline)
        if result is not None:
            results.append(result)
    return results
