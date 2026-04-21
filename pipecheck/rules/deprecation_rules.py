from dataclasses import dataclass
from datetime import datetime
from pipecheck.rules.base import Rule, LintResult, Severity


@dataclass
class NoDeprecationPolicyRule(Rule):
    name: str = "no_deprecation_policy"
    description: str = "Pipeline should define a deprecation policy"

    def check(self, pipeline) -> LintResult:
        policy = getattr(pipeline, "deprecation_policy", None)
        if not policy:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="Pipeline has no deprecation policy defined",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")


@dataclass
class InvalidDeprecationDateRule(Rule):
    name: str = "invalid_deprecation_date"
    description: str = "Deprecation date must be a valid ISO 8601 date string"

    def check(self, pipeline) -> LintResult:
        policy = getattr(pipeline, "deprecation_policy", None)
        if not isinstance(policy, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="OK")
        date_str = policy.get("deprecate_on")
        if not date_str:
            return LintResult(rule=self.name, severity=Severity.OK, message="OK")
        try:
            datetime.fromisoformat(str(date_str))
        except ValueError:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Deprecation date '{date_str}' is not a valid ISO 8601 date",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")


@dataclass
class DeprecatedPipelineActiveRule(Rule):
    name: str = "deprecated_pipeline_active"
    description: str = "Pipeline past its deprecation date should not be active"

    def check(self, pipeline) -> LintResult:
        policy = getattr(pipeline, "deprecation_policy", None)
        if not isinstance(policy, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="OK")
        date_str = policy.get("deprecate_on")
        active = getattr(pipeline, "active", True)
        if not date_str or not active:
            return LintResult(rule=self.name, severity=Severity.OK, message="OK")
        try:
            deprecate_on = datetime.fromisoformat(str(date_str)).date()
        except ValueError:
            return LintResult(rule=self.name, severity=Severity.OK, message="OK")
        if deprecate_on <= datetime.utcnow().date():
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Pipeline is active but passed its deprecation date ({date_str})",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")


@dataclass
class NoDeprecationOwnerRule(Rule):
    name: str = "no_deprecation_owner"
    description: str = "Deprecation policy should specify a responsible owner"

    def check(self, pipeline) -> LintResult:
        policy = getattr(pipeline, "deprecation_policy", None)
        if not isinstance(policy, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="OK")
        owner = policy.get("owner")
        if not owner or not str(owner).strip():
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="Deprecation policy does not specify an owner",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")
