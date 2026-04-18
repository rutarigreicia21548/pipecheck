from typing import Any, List, Optional
from pipecheck.rules.base import LintResult, Rule
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
from pipecheck.rules.alert_rules import NoAlertRule, InvalidAlertChannelRule, TooManyAlertsRule
from pipecheck.rules.sla_rules import NoSLARule, SLATooLongRule, ZeroSLARule
from pipecheck.rules.label_rules import NoLabelsRule, TooManyLabelsRule, InvalidLabelFormatRule
from pipecheck.rules.resource_rules import NoMemoryLimitRule, MemoryLimitTooHighRule, NoCPULimitRule
from pipecheck.rules.notification_rules import NoNotificationRule, InvalidNotificationTypeRule, InvalidNotificationEventRule
from pipecheck.rules.version_rules import NoVersionRule, InvalidVersionFormatRule, MajorVersionZeroRule
from pipecheck.rules.metadata_rules import NoMetadataRule, InvalidMetadataTypeRule, EmptyMetadataRule
from pipecheck.rules.access_rules import NoAccessLevelRule, InvalidAccessLevelRule, NoAllowedRolesRule
from pipecheck.rules.data_quality_rules import NoDataQualityChecksRule, InvalidCheckTypeRule, TooManyChecksRule
from pipecheck.rules.checkpoint_rules import NoCheckpointRule, InvalidCheckpointIntervalRule, CheckpointIntervalTooLargeRule
from pipecheck.rules.lineage_rules import NoLineageRule, MissingLineageInputsRule, MissingLineageOutputsRule, InvalidLineageDatasetRule


DEFAULT_RULES: List[Rule] = [
    NoPipelineIdRule(), InvalidIdCharactersRule(), NoTagsRule(),
    NoScheduleRule(), InvalidCronScheduleRule(), FrequentScheduleRule(),
    SnakeCaseIdRule(), IdTooLongRule(), TagNamingRule(),
    NoDependenciesRule(), CircularDependencyRule(), TooManyDependenciesRule(),
    NoRetriesRule(), TooManyRetriesRule(), NoRetryDelayRule(),
    NoTimeoutRule(), TimeoutTooLongRule(), ZeroTimeoutRule(),
    NoOwnerRule(), InvalidOwnerFormatRule(), GenericOwnerRule(),
    NoDescriptionRule(), ShortDescriptionRule(), NoOwnerContactRule(),
    NoEnvironmentRule(), InvalidEnvironmentRule(), ProductionWithoutOwnerRule(),
    NoConcurrencyLimitRule(), ConcurrencyTooHighRule(), ZeroConcurrencyRule(),
    NoAlertRule(), InvalidAlertChannelRule(), TooManyAlertsRule(),
    NoSLARule(), SLATooLongRule(), ZeroSLARule(),
    NoLabelsRule(), TooManyLabelsRule(), InvalidLabelFormatRule(),
    NoMemoryLimitRule(), MemoryLimitTooHighRule(), NoCPULimitRule(),
    NoNotificationRule(), InvalidNotificationTypeRule(), InvalidNotificationEventRule(),
    NoVersionRule(), InvalidVersionFormatRule(), MajorVersionZeroRule(),
    NoMetadataRule(), InvalidMetadataTypeRule(), EmptyMetadataRule(),
    NoAccessLevelRule(), InvalidAccessLevelRule(), NoAllowedRolesRule(),
    NoDataQualityChecksRule(), InvalidCheckTypeRule(), TooManyChecksRule(),
    NoCheckpointRule(), InvalidCheckpointIntervalRule(), CheckpointIntervalTooLargeRule(),
    NoLineageRule(), MissingLineageInputsRule(), MissingLineageOutputsRule(), InvalidLineageDatasetRule(),
]


def run_rules(pipeline: Any, rules: Optional[List[Rule]] = None) -> List[LintResult]:
    active_rules = rules if rules is not None else DEFAULT_RULES
    return [rule.check(pipeline) for rule in active_rules]
