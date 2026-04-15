from dataclasses import dataclass
from typing import Any

from pipecheck.rules.base import LintResult, Rule, Severity


@dataclass
class NoDependenciesRule(Rule):
    """Warn when a pipeline declares no upstream or downstream dependencies."""

    id: str = "no-dependencies"
    description: str = "Pipeline has no declared dependencies"
    severity: Severity = Severity.WARNING

    def check(self, pipeline: Any) -> LintResult | None:
        deps = getattr(pipeline, "dependencies", None)
        if not deps:
            return LintResult(
                rule_id=self.id,
                severity=self.severity,
                message="Pipeline declares no dependencies; consider documenting upstream sources.",
            )
        return None


@dataclass
class CircularDependencyRule(Rule):
    """Error when a pipeline lists itself as one of its own dependencies."""

    id: str = "circular-dependency"
    description: str = "Pipeline must not depend on itself"
    severity: Severity = Severity.ERROR

    def check(self, pipeline: Any) -> LintResult | None:
        pipeline_id = getattr(pipeline, "id", None) or getattr(pipeline, "name", None)
        deps = getattr(pipeline, "dependencies", None) or []
        if pipeline_id and pipeline_id in deps:
            return LintResult(
                rule_id=self.id,
                severity=self.severity,
                message=f"Pipeline '{pipeline_id}' lists itself as a dependency.",
            )
        return None


@dataclass
class TooManyDependenciesRule(Rule):
    """Warn when a pipeline declares an unusually large number of dependencies."""

    id: str = "too-many-dependencies"
    description: str = "Pipeline has an excessive number of dependencies"
    severity: Severity = Severity.WARNING
    max_dependencies: int = 10

    def check(self, pipeline: Any) -> LintResult | None:
        deps = getattr(pipeline, "dependencies", None) or []
        if len(deps) > self.max_dependencies:
            return LintResult(
                rule_id=self.id,
                severity=self.severity,
                message=(
                    f"Pipeline has {len(deps)} dependencies "
                    f"(max recommended: {self.max_dependencies})."
                ),
            )
        return None
