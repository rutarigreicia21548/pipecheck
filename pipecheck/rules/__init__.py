from typing import List, Any
from pipecheck.rules.base import LintResult, Rule
from pipecheck.rules.common_rules import NoPipelineIdRule, InvalidIdCharactersRule, NoTagsRule
from pipecheck.rules.schedule_rules import NoScheduleRule, InvalidCronScheduleRule, FrequentScheduleRule
from pipecheck.rules.naming_rules import SnakeCaseIdRule, IdTooLongRule, TagNamingRule
from pipecheck.rules.dependency_rules import NoDependenciesRule, CircularDependencyRule, TooManyDependenciesRule
from pipecheck.rules.retries_rules import NoRetriesRule, TooManyRetriesRule, NoRetryDelayRule


DEFAULT_RULES: List[Rule] = [
    NoPipelineIdRule(),
    InvalidIdCharactersRule(),
    NoTagsRule(),
    NoScheduleRule(),
    InvalidCronScheduleRule(),
    FrequentScheduleRule(),
    SnakeCaseIdRule(),
    IdTooLongRule(),
    TagNamingRule(),
    NoDependenciesRule(),
    CircularDependencyRule(),
    TooManyDependenciesRule(),
    NoRetriesRule(),
    TooManyRetriesRule(),
    NoRetryDelayRule(),
]


def run_rules(
    pipeline: Any,
    rules: List[Rule] = None,
) -> List[LintResult]:
    """Run all rules (or a custom list) against a pipeline object.

    Args:
        pipeline: A parsed pipeline object (AirflowDAG, PrefectFlow, etc.).
        rules: Optional list of Rule instances to run. Defaults to DEFAULT_RULES.

    Returns:
        A list of LintResult objects, one per rule.
    """
    active_rules = rules if rules is not None else DEFAULT_RULES
    results: List[LintResult] = []
    for rule in active_rules:
        try:
            result = rule.check(pipeline)
            results.append(result)
        except Exception as exc:  # pragma: no cover
            results.append(
                LintResult(
                    rule=rule.name,
                    severity=rule.severity,
                    message=f"Rule '{rule.name}' raised an unexpected error: {exc}",
                    passed=False,
                )
            )
    return results
