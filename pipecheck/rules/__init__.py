from pipecheck.rules.common_rules import NoPipelineIdRule, InvalidIdCharactersRule, NoTagsRule
from pipecheck.rules.schedule_rules import NoScheduleRule, InvalidCronScheduleRule, FrequentScheduleRule
from pipecheck.rules.naming_rules import SnakeCaseIdRule, IdTooLongRule, TagNamingRule
from pipecheck.rules.dependency_rules import NoDependenciesRule, CircularDependencyRule, TooManyDependenciesRule
from pipecheck.rules.retries_rules import NoRetriesRule, TooManyRetriesRule, NoRetryDelayRule
from pipecheck.rules.timeout_rules import NoTimeoutRule, TimeoutTooLongRule, ZeroTimeoutRule
from pipecheck.rules.owner_rules import NoOwnerRule, InvalidOwnerFormatRule, GenericOwnerRule
from pipecheck.rules.doc_rules import NoDescriptionRule, ShortDescriptionRule, NoOwnerContactRule
from pipecheck.rules.env_rules import NoEnvironmentRule, InvalidEnvironmentRule, ProductionWithoutOwnerRule
from pipecheck.rules.base import LintResult
from typing import List, Type

DEFAULT_RULES = [
    NoPipelineIdRule,
    InvalidIdCharactersRule,
    NoTagsRule,
    NoScheduleRule,
    InvalidCronScheduleRule,
    FrequentScheduleRule,
    SnakeCaseIdRule,
    IdTooLongRule,
    TagNamingRule,
    NoDependenciesRule,
    CircularDependencyRule,
    TooManyDependenciesRule,
    NoRetriesRule,
    TooManyRetriesRule,
    NoRetryDelayRule,
    NoTimeoutRule,
    TimeoutTooLongRule,
    ZeroTimeoutRule,
    NoOwnerRule,
    InvalidOwnerFormatRule,
    GenericOwnerRule,
    NoDescriptionRule,
    ShortDescriptionRule,
    NoOwnerContactRule,
    NoEnvironmentRule,
    InvalidEnvironmentRule,
    ProductionWithoutOwnerRule,
]


def run_rules(pipeline, rules: List[Type] = None) -> List[LintResult]:
    if rules is None:
        rules = DEFAULT_RULES
    results = []
    for rule_cls in rules:
        rule = rule_cls()
        results.append(rule.check(pipeline))
    return results
