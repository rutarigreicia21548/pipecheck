from typing import List, Type
from pipecheck.rules.base import Rule, LintResult
from pipecheck.rules.common_rules import NoPipelineIdRule, InvalidIdCharactersRule, NoTagsRule
from pipecheck.rules.schedule_rules import NoScheduleRule, InvalidCronScheduleRule, FrequentScheduleRule
from pipecheck.rules.naming_rules import SnakeCaseIdRule, IdTooLongRule, TagNamingRule
from pipecheck.rules.dependency_rules import NoDependenciesRule, CircularDependencyRule, TooManyDependenciesRule
from pipecheck.rules.retries_rules import NoRetriesRule, TooManyRetriesRule, NoRetryDelayRule
from pipecheck.rules.timeout_rules import NoTimeoutRule, TimeoutTooLongRule, ZeroTimeoutRule
from pipecheck.rules.owner_rules import NoOwnerRule, InvalidOwnerFormatRule, GenericOwnerRule
from pipecheck.rules.doc_rules import NoDescriptionRule, ShortDescriptionRule, NoOwnerContactRule
from pipecheck.rules.env_rules import NoEnvironmentRule, InvalidEnvironmentRule, ProductionWithoutOwnerRule
from pipecheck.rules.concurrency_rules import NoConcurrencyLimitRule, ConcurrencyTooHighRule, ZeroConcurrencyRule

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
    NoDescriptionRule(),
    ShortDescriptionRule(),
    NoOwnerContactRule(),
    NoEnvironmentRule(),
    InvalidEnvironmentRule(),
    ProductionWithoutOwnerRule(),
    NoConcurrencyLimitRule(),
    ConcurrencyTooHighRule(),
    ZeroConcurrencyRule(),
]


def run_rules(pipeline, rules: List[Rule] = None) -> List[LintResult]:
    active_rules = rules if rules is not None else DEFAULT_RULES
    return [rule.check(pipeline) for rule in active_rules]
