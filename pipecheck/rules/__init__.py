from typing import List, Optional, Type
from pipecheck.rules.base import Rule, LintResult
from pipecheck.rules.common_rules import NoPipelineIdRule, InvalidIdCharactersRule, NoTagsRule
from pipecheck.rules.schedule_rules import NoScheduleRule, InvalidCronScheduleRule, FrequentScheduleRule
from pipecheck.rules.naming_rules import SnakeCaseIdRule, IdTooLongRule, TagNamingRule
from pipecheck.rules.dependency_rules import NoDependenciesRule, CircularDependencyRule, TooManyDependenciesRule
from pipecheck.rules.retries_rules import NoRetriesRule, TooManyRetriesRule, NoRetryDelayRule
from pipecheck.rules.timeout_rules import NoTimeoutRule, TimeoutTooLongRule, ZeroTimeoutRule
from pipecheck.rules.owner_rules import NoOwnerRule, InvalidOwnerFormatRule, GenericOwnerRule

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
    NoTimeoutRule(),
    TimeoutTooLongRule(),
    ZeroTimeoutRule(),
    NoOwnerRule(),
    InvalidOwnerFormatRule(),
    GenericOwnerRule(),
]


def run_rules(
    pipeline,
    rules: Optional[List[Rule]] = None,
) -> List[LintResult]:
    """Run all rules (or a custom list) against a pipeline object.

    Args:
        pipeline: Any pipeline object with the expected attributes.
        rules: Optional list of Rule instances. Defaults to DEFAULT_RULES.

    Returns:
        List of LintResult objects, one per rule.
    """
    active_rules = rules if rules is not None else DEFAULT_RULES
    return [rule.check(pipeline) for rule in active_rules]
