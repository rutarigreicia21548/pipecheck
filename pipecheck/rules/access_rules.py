from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity

VALID_ACCESS_LEVELS = {"public", "internal", "restricted", "private"}
MAX_ALLOWED_ROLES = 10


@dataclass
class NoAccessLevelRule(Rule):
    name: str = "no_access_level"
    description: str = "Pipeline should define an access level"

    def check(self, pipeline) -> LintResult:
        level = getattr(pipeline, "access_level", None)
        if not level:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="No access level defined; defaulting to unrestricted access",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")


@dataclass
class InvalidAccessLevelRule(Rule):
    name: str = "invalid_access_level"
    description: str = "Access level must be one of the recognised values"

    def check(self, pipeline) -> LintResult:
        level = getattr(pipeline, "access_level", None)
        if level and level not in VALID_ACCESS_LEVELS:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Invalid access level '{level}'; must be one of {sorted(VALID_ACCESS_LEVELS)}",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")


@dataclass
class NoAllowedRolesRule(Rule):
    name: str = "no_allowed_roles"
    description: str = "Restricted/private pipelines should define allowed roles"

    def check(self, pipeline) -> LintResult:
        level = getattr(pipeline, "access_level", None)
        roles = getattr(pipeline, "allowed_roles", None)
        if level in {"restricted", "private"} and not roles:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Pipeline with access level '{level}' must specify allowed_roles",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")


@dataclass
class TooManyRolesRule(Rule):
    name: str = "too_many_roles"
    description: str = f"allowed_roles should not exceed {MAX_ALLOWED_ROLES} entries"

    def check(self, pipeline) -> LintResult:
        roles = getattr(pipeline, "allowed_roles", None)
        if roles and len(roles) > MAX_ALLOWED_ROLES:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message=f"allowed_roles has {len(roles)} entries; consider reducing to {MAX_ALLOWED_ROLES} or fewer",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")
