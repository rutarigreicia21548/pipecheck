from __future__ import annotations

from typing import Any

from pipecheck.rules.access_rules import InvalidAccessLevelRule, NoAccessLevelRule, NoAllowedRolesRule
from pipecheck.rules.alert_rules import InvalidAlertChannelRule, NoAlertRule, TooManyAlertsRule
from pipecheck.rules.audit_rules import AuditRetentionTooLongRule, InvalidAuditLevelRule, NoAuditConfigRule
from pipecheck.rules.backfill_rules import BackfillWindowTooLargeRule, InvalidBackfillStrategyRule, NoBackfillConfigRule
from pipecheck.rules.base import LintResult
from pipecheck.rules.cache_rules import CacheTTLTooLongRule, InvalidCacheStrategyRule, NoCacheStrategyRule
from pipecheck.rules.checkpoint_rules import CheckpointIntervalTooLargeRule, InvalidCheckpointIntervalRule, NoCheckpointRule
from pipecheck.rules.common_rules import InvalidIdCharactersRule, NoPipelineIdRule, NoTagsRule
from pipecheck.rules.compliance_rules import InvalidComplianceTagRule, NoComplianceTagRule, PiiWithoutOwnerRule
from pipecheck.rules.concurrency_rules import ConcurrencyTooHighRule, NoConcurrencyLimitRule, ZeroConcurrencyRule
from pipecheck.rules.cost_rules import CostEstimateTooHighRule, InvalidCostTierRule, NoCostEstimateRule
from pipecheck.rules.data_quality_rules import InvalidCheckTypeRule, NoDataQualityChecksRule, TooManyChecksRule
from pipecheck.rules.dependency_rules import CircularDependencyRule, NoDependenciesRule, TooManyDependenciesRule
from pipecheck.rules.deprecation_rules import (
    DeprecatedPipelineActiveRule,
    DeprecationSoonRule,
    InvalidDeprecationDateRule,
    NoDeprecationPolicyRule,
)
from pipecheck.rules.doc_rules import NoDescriptionRule, NoOwnerContactRule, ShortDescriptionRule
from pipecheck.rules.encryption_rules import NoEncryptionRule, UnrecognizedEncryptionRule, WeakEncryptionRule
from pipecheck.rules.env_rules import InvalidEnvironmentRule, NoEnvironmentRule, ProductionWithoutOwnerRule
from pipecheck.rules.idempotency_rules import IdempotencyWithoutKeyRule, InvalidIdempotencyStrategyRule, NoIdempotencyRule
from pipecheck.rules.label_rules import InvalidLabelFormatRule, NoLabelsRule, TooManyLabelsRule
from pipecheck.rules.lineage_rules import MissingLineageInputsRule, MissingLineageOutputsRule, NoLineageRule
from pipecheck.rules.logging_rules import InvalidLogLevelRule, LogRetentionTooLongRule, NoLoggingConfigRule
from pipecheck.rules.metadata_rules import EmptyMetadataRule, InvalidMetadataTypeRule, NoMetadataRule
from pipecheck.rules.naming_rules import IdTooLongRule, SnakeCaseIdRule, TagNamingRule
from pipecheck.rules.notification_rules import InvalidNotificationEventRule, InvalidNotificationTypeRule, NoNotificationRule
from pipecheck.rules.owner_rules import GenericOwnerRule, InvalidOwnerFormatRule, NoOwnerRule
from pipecheck.rules.parallelism_rules import NoParallelismRule, ParallelismTooHighRule, ZeroParallelismRule
from pipecheck.rules.priority_rules import InvalidPriorityLevelRule, NoPriorityRule, PriorityWeightTooHighRule
from pipecheck.rules.resource_rules import MemoryLimitTooHighRule, NoCPULimitRule, NoMemoryLimitRule
from pipecheck.rules.retries_rules import NoRetriesRule, NoRetryDelayRule, TooManyRetriesRule
from pipecheck.rules.runtime_rules import NoRuntimeLimitRule, RuntimeTooLongRule, RuntimeWarnThresholdRule
from pipecheck.rules.schedule_rules import FrequentScheduleRule, InvalidCronScheduleRule, NoScheduleRule
from pipecheck.rules.secrets_rules import InsecureSecretBackendRule, InvalidSecretBackendRule, NoSecretsConfigRule
from pipecheck.rules.sla_rules import NoSLARule, SLATooLongRule, ZeroSLARule
from pipecheck.rules.timeout_rules import NoTimeoutRule, TimeoutTooLongRule, ZeroTimeoutRule
from pipecheck.rules.trigger_rules import InvalidTriggerTypeRule, NoTriggerRule, TooManyTriggerConditionsRule
from pipecheck.rules.version_rules import InvalidVersionFormatRule, MajorVersionZeroRule, NoVersionRule

_DEFAULT_RULES = [
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
    NoLineageRule(), MissingLineageInputsRule(), MissingLineageOutputsRule(),
    NoTriggerRule(), InvalidTriggerTypeRule(), TooManyTriggerConditionsRule(),
    NoCostEstimateRule(), CostEstimateTooHighRule(), InvalidCostTierRule(),
    NoComplianceTagRule(), InvalidComplianceTagRule(), PiiWithoutOwnerRule(),
    NoCacheStrategyRule(), InvalidCacheStrategyRule(), CacheTTLTooLongRule(),
    NoParallelismRule(), ParallelismTooHighRule(), ZeroParallelismRule(),
    NoBackfillConfigRule(), InvalidBackfillStrategyRule(), BackfillWindowTooLargeRule(),
    NoIdempotencyRule(), InvalidIdempotencyStrategyRule(), IdempotencyWithoutKeyRule(),
    NoLoggingConfigRule(), InvalidLogLevelRule(), LogRetentionTooLongRule(),
    NoRuntimeLimitRule(), RuntimeTooLongRule(), RuntimeWarnThresholdRule(),
    NoPriorityRule(), InvalidPriorityLevelRule(), PriorityWeightTooHighRule(),
    NoEncryptionRule(), WeakEncryptionRule(), UnrecognizedEncryptionRule(),
    NoAuditConfigRule(), InvalidAuditLevelRule(), AuditRetentionTooLongRule(),
    NoDeprecationPolicyRule(), InvalidDeprecationDateRule(), DeprecatedPipelineActiveRule(), DeprecationSoonRule(),
    NoSecretsConfigRule(), InvalidSecretBackendRule(), InsecureSecretBackendRule(),
]


def run_rules(pipeline: Any, rules: list | None = None) -> list[LintResult]:
    """Run all (or a custom list of) rules against *pipeline* and return results."""
    active_rules = rules if rules is not None else _DEFAULT_RULES
    return [rule.check(pipeline) for rule in active_rules]
