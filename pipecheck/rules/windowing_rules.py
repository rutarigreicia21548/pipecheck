from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pipecheck.rules.base import LintResult, Rule, Severity

VALID_WINDOW_TYPES = {"tumbling", "sliding", "session", "global"}
VALID_WINDOW_UNITS = {"seconds", "minutes", "hours", "days"}
MAX_WINDOW_SIZE_SECONDS = 7 * 24 * 3600  # 7 days


@dataclass
class NoWindowingConfigRule(Rule):
    name: str = "no_windowing_config"
    description: str = "Pipeline has no windowing configuration"

    def check(self, pipeline: Any) -> LintResult:
        value = getattr(pipeline, "windowing", None)
        if not value:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="No windowing configuration defined; consider adding one for streaming pipelines.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=Severity.INFO, message="Windowing config present.", passed=True)


@dataclass
class InvalidWindowTypeRule(Rule):
    name: str = "invalid_window_type"
    description: str = "Window type must be one of the recognised strategies"

    def check(self, pipeline: Any) -> LintResult:
        windowing = getattr(pipeline, "windowing", None)
        if not isinstance(windowing, dict):
            return LintResult(rule=self.name, severity=Severity.INFO, message="No windowing dict to validate.", passed=True)
        window_type = windowing.get("type")
        if window_type and window_type not in VALID_WINDOW_TYPES:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Invalid window type '{window_type}'. Must be one of: {sorted(VALID_WINDOW_TYPES)}.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=Severity.INFO, message="Window type is valid.", passed=True)


@dataclass
class WindowSizeTooLargeRule(Rule):
    name: str = "window_size_too_large"
    description: str = "Window size must not exceed 7 days"
    max_seconds: int = MAX_WINDOW_SIZE_SECONDS

    def check(self, pipeline: Any) -> LintResult:
        windowing = getattr(pipeline, "windowing", None)
        if not isinstance(windowing, dict):
            return LintResult(rule=self.name, severity=Severity.INFO, message="No windowing dict to validate.", passed=True)
        size = windowing.get("size")
        unit = windowing.get("unit", "seconds")
        if size is None:
            return LintResult(rule=self.name, severity=Severity.INFO, message="No window size to validate.", passed=True)
        multipliers = {"seconds": 1, "minutes": 60, "hours": 3600, "days": 86400}
        factor = multipliers.get(unit, 1)
        total_seconds = size * factor
        if total_seconds > self.max_seconds:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Window size {size} {unit} exceeds maximum of 7 days.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=Severity.INFO, message="Window size is within limits.", passed=True)


@dataclass
class InvalidWindowUnitRule(Rule):
    name: str = "invalid_window_unit"
    description: str = "Window unit must be a recognised time unit"

    def check(self, pipeline: Any) -> LintResult:
        windowing = getattr(pipeline, "windowing", None)
        if not isinstance(windowing, dict):
            return LintResult(rule=self.name, severity=Severity.INFO, message="No windowing dict to validate.", passed=True)
        unit = windowing.get("unit")
        if unit and unit not in VALID_WINDOW_UNITS:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Invalid window unit '{unit}'. Must be one of: {sorted(VALID_WINDOW_UNITS)}.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=Severity.INFO, message="Window unit is valid.", passed=True)
