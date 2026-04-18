from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity

VALID_TRIGGER_TYPES = {"manual", "scheduled", "event", "sensor", "webhook"}
MAX_TRIGGER_CONDITIONS = 10


@dataclass
class NoTriggerRule(Rule):
    name: str = "no-trigger"
    description: str = "Pipeline should define a trigger type"

    def check(self, pipeline) -> LintResult:
        trigger = getattr(pipeline, "trigger", None)
        if not trigger:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="No trigger defined for pipeline",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Trigger is defined")


@dataclass
class InvalidTriggerTypeRule(Rule):
    name: str = "invalid-trigger-type"
    description: str = "Trigger type must be one of the valid types"

    def check(self, pipeline) -> LintResult:
        trigger = getattr(pipeline, "trigger", None)
        if not trigger:
            return LintResult(rule=self.name, severity=Severity.OK, message="No trigger to validate")
        trigger_type = trigger if isinstance(trigger, str) else trigger.get("type", "")
        if trigger_type not in VALID_TRIGGER_TYPES:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Invalid trigger type '{trigger_type}'. Must be one of: {sorted(VALID_TRIGGER_TYPES)}",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Trigger type is valid")


@dataclass
class TooManyTriggerConditionsRule(Rule):
    name: str = "too-many-trigger-conditions"
    description: str = f"Trigger should not have more than {MAX_TRIGGER_CONDITIONS} conditions"
    max_conditions: int = MAX_TRIGGER_CONDITIONS

    def check(self, pipeline) -> LintResult:
        trigger = getattr(pipeline, "trigger", None)
        if not trigger or isinstance(trigger, str):
            return LintResult(rule=self.name, severity=Severity.OK, message="No conditions to validate")
        conditions = trigger.get("conditions", [])
        if len(conditions) > self.max_conditions:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message=f"Trigger has {len(conditions)} conditions, max recommended is {self.max_conditions}",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Trigger condition count is acceptable")
