from typing import Any

from pipecheck.rules.base import LintResult, Rule
from pipecheck.rules.common_rules import (
    InvalidIdCharactersRule,
    NoPipelineIdRule,
    NoTagsRule,
)
from pipecheck.rules.dependency_rules import (
    CircularDependencyRule,
    NoDependenciesRule,
    TooManyDependenciesRule,
)
from pipecheck.rules.naming_rules import (
    IdTooLongRule,
    SnakeCaseIdRule,
    TagNamingRule,
)
from pipecheck.rules.schedule_rules import (
    FrequentScheduleRule,
    InvalidCronScheduleRule,
    NoScheduleRule,
)

DEFAULT_RULES: list[Rule] = [
    # Common
    NoPipelineIdRule(),
    InvalidIdCharactersRule(),
    NoTagsRule(),
    # Naming
    SnakeCaseIdRule(),
    IdTooLongRule(),
    TagNamingRule(),
    # Schedule
    NoScheduleRule(),
    InvalidCronScheduleRule(),
    FrequentScheduleRule(),
    # Dependencies
    NoDependenciesRule(),
    CircularDependencyRule(),
    TooManyDependenciesRule(),
]


def run_rules(
    pipeline: Any,
    rules: list[Rule] | None = None,
) -> list[LintResult]:
    """Run all rules (or a custom list) against *pipeline* and return violations."""
    active_rules = rules if rules is not None else DEFAULT_RULES
    results: list[LintResult] = []
    for rule in active_rules:
        result = rule.check(pipeline)
        if result is not None:
            results.append(result)
    return results
