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
from pipecheck.rules.lineage_rules import NoLineageRule, MissingLineageInputsRule, MissingLineageOutputsRule
from pipecheck.rules.trigger_rules import NoTriggerRule, InvalidTriggerTypeRule, TooManyTriggerConditionsRule
from pipecheck.rules.cost_rules import NoCostEstimateRule, CostEstimateTooHighRule, InvalidCostTierRule
from pipecheck.rules.compliance_rules import NoComplianceTagRule, InvalidComplianceTagRule, PiiWithoutOwnerRule
from pipecheck.rules.cache_rules import NoCacheStrategyRule, InvalidCacheStrategyRule, CacheTTLTooLongRule
from pipecheck.rules.parallelism_rules import NoParallelismRule, ParallelismTooHighRule, ZeroParallelismRule
from pipecheck.rules.backfill_rules import NoBackfillConfigRule, InvalidBackfillStrategyRule, BackfillWindowTooLargeRule
from pipecheck.rules.idempotency_rules import NoIdempotencyRule, InvalidIdempotencyStrategyRule, IdempotencyWithoutKeyRule
from pipecheck.rules.logging_rules import NoLoggingConfigRule, InvalidLogLevelRule, LogRetentionTooLongRule
from pipecheck.rules.runtime_rules import NoRuntimeLimitRule, RuntimeTooLongRule, RuntimeWarnThresholdRule
from pipecheck.rules.priority_rules import NoPriorityRule, InvalidPriorityLevelRule, PriorityWeightTooHighRule
from pipecheck.rules.encryption_rules import NoEncryptionRule, WeakEncryptionRule, UnrecognizedEncryptionRule
from pipecheck.rules.audit_rules import NoAuditConfigRule, InvalidAuditLevelRule, AuditRetentionTooLongRule
from pipecheck.rules.deprecation_rules import NoDeprecationPolicyRule, InvalidDeprecationDateRule, DeprecatedPipelineActiveRule
from pipecheck.rules.secrets_rules import NoSecretsConfigRule, InvalidSecretBackendRule, InsecureSecretBackendRule
from pipecheck.rules.rollback_rules import NoRollbackConfigRule, InvalidRollbackStrategyRule, RollbackWindowTooLargeRule
from pipecheck.rules.observability_rules import (
    NoObservabilityConfigRule,
    InvalidTracingBackendRule,
    InvalidMetricsBackendRule,
    TooManyCustomMetricsRule,
)

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
    NoDeprecationPolicyRule(), InvalidDeprecationDateRule(), DeprecatedPipelineActiveRule(),
    NoSecretsConfigRule(), InvalidSecretBackendRule(), InsecureSecretBackendRule(),
    NoRollbackConfigRule(), InvalidRollbackStrategyRule(), RollbackWindowTooLargeRule(),
    NoObservabilityConfigRule(), InvalidTracingBackendRule(),
    InvalidMetricsBackendRule(), TooManyCustomMetricsRule(),
]


def run_rules(pipeline, rules=None):
    """Run all rules (or a provided subset) against a pipeline object."""
    active_rules = rules if rules is not None else _DEFAULT_RULES
    return [rule.check(pipeline) for rule in active_rules]
