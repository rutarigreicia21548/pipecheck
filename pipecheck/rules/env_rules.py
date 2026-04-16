from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity

ALLOWED_ENVS = {"dev", "staging", "prod", "production", "development", "test"}


@dataclass
class NoEnvironmentRule(Rule):
    name: str = "no-environment"
    description: str = "Pipeline should specify a target environment"
    severity: Severity = Severity.WARNING

    def check(self, pipeline) -> LintResult:
        env = getattr(pipeline, "environment", None)
        if not env:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message="No environment specified for pipeline",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)


@dataclass
class InvalidEnvironmentRule(Rule):
    name: str = "invalid-environment"
    description: str = "Pipeline environment must be a recognised value"
    severity: Severity = Severity.ERROR

    def check(self, pipeline) -> LintResult:
        env = getattr(pipeline, "environment", None)
        if env and env.lower() not in ALLOWED_ENVS:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=f"Unknown environment '{env}'. Allowed: {sorted(ALLOWED_ENVS)}",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)


@dataclass
class ProductionWithoutOwnerRule(Rule):
    name: str = "prod-requires-owner"
    description: str = "Production pipelines must have an owner"
    severity: Severity = Severity.ERROR

    def check(self, pipeline) -> LintResult:
        env = getattr(pipeline, "environment", None)
        owner = getattr(pipeline, "owner", None)
        if env and env.lower() in {"prod", "production"} and not owner:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message="Production pipeline must specify an owner",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
