"""Base classes for pipecheck lint rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class LintResult:
    rule_id: str
    severity: Severity
    message: str
    pipeline_id: str
    details: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.pipeline_id}: {self.message} ({self.rule_id})"


class Rule:
    """Abstract base class for all lint rules."""

    rule_id: str = ""
    severity: Severity = Severity.WARNING
    description: str = ""

    def check(self, pipeline: Any) -> list[LintResult]:
        """Run the rule against a pipeline object. Returns a list of LintResults."""
        raise NotImplementedError

    def _result(self, pipeline_id: str, message: str, **details: Any) -> LintResult:
        return LintResult(
            rule_id=self.rule_id,
            severity=self.severity,
            message=message,
            pipeline_id=pipeline_id,
            details=details,
        )
