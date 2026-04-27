from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pipecheck.rules.base import LintResult, Rule, Severity

VALID_ISOLATION_LEVELS = {"none", "process", "container", "vm", "sandbox"}
INSECURE_ISOLATION_LEVELS = {"none"}
MAX_SHARED_RESOURCES = 10


@dataclass
class NoIsolationConfigRule(Rule):
    name: str = "no_isolation_config"
    description: str = "Pipeline should define an isolation configuration."

    def check(self, pipeline: Any) -> LintResult:
        isolation = getattr(pipeline, "isolation", None)
        if not isolation:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="No isolation config defined; pipeline may share resources unsafely.",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Isolation config present.")


@dataclass
class InvalidIsolationLevelRule(Rule):
    name: str = "invalid_isolation_level"
    description: str = "Isolation level must be one of the recognised values."

    def check(self, pipeline: Any) -> LintResult:
        isolation = getattr(pipeline, "isolation", None)
        if not isolation or not isinstance(isolation, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="Skipped.")
        level = isolation.get("level", "")
        if level and level not in VALID_ISOLATION_LEVELS:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Isolation level '{level}' is not valid. Choose from: {sorted(VALID_ISOLATION_LEVELS)}.",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Isolation level is valid.")


@dataclass
class InsecureIsolationLevelRule(Rule):
    name: str = "insecure_isolation_level"
    description: str = "Pipelines should not use insecure isolation levels in production."

    def check(self, pipeline: Any) -> LintResult:
        isolation = getattr(pipeline, "isolation", None)
        if not isolation or not isinstance(isolation, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="Skipped.")
        level = isolation.get("level", "")
        if level in INSECURE_ISOLATION_LEVELS:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message=f"Isolation level '{level}' is considered insecure for production workloads.",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Isolation level is sufficiently secure.")


@dataclass
class TooManySharedResourcesRule(Rule):
    name: str = "too_many_shared_resources"
    description: str = f"Pipelines should not share more than {MAX_SHARED_RESOURCES} resources."

    def check(self, pipeline: Any) -> LintResult:
        isolation = getattr(pipeline, "isolation", None)
        if not isolation or not isinstance(isolation, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="Skipped.")
        shared = isolation.get("shared_resources", [])
        if isinstance(shared, list) and len(shared) > MAX_SHARED_RESOURCES:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message=f"Pipeline shares {len(shared)} resources; limit is {MAX_SHARED_RESOURCES}.",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Shared resource count is acceptable.")
