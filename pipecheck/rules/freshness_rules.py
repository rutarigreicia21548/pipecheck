from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pipecheck.rules.base import LintResult, Rule, Severity

# Maximum allowed data freshness SLA in hours
MAX_FRESHNESS_HOURS = 168  # 7 days

VALID_FRESHNESS_UNITS = {"seconds", "minutes", "hours", "days"}


class NoFreshnessConfigRule(Rule):
    """Pipelines should declare a data freshness requirement."""

    name = "no-freshness-config"
    description = "Pipeline does not define a data freshness requirement."

    def check(self, pipeline: Any) -> LintResult:
        freshness = getattr(pipeline, "freshness", None)
        if not freshness:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="No data freshness config defined; consumers cannot determine staleness tolerance.",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Freshness config present.")


class InvalidFreshnessUnitRule(Rule):
    """Freshness unit must be one of the recognised time units."""

    name = "invalid-freshness-unit"
    description = "Freshness unit is not a recognised time unit."

    def check(self, pipeline: Any) -> LintResult:
        freshness = getattr(pipeline, "freshness", None)
        if not isinstance(freshness, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="Skipped — no freshness dict.")
        unit = freshness.get("unit", "")
        if unit not in VALID_FRESHNESS_UNITS:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=(
                    f"Invalid freshness unit '{unit}'. "
                    f"Must be one of: {sorted(VALID_FRESHNESS_UNITS)}."
                ),
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Freshness unit is valid.")


class FreshnessTooLenientRule(Rule):
    """Freshness threshold must not exceed the maximum allowed value."""

    name = "freshness-too-lenient"
    description = f"Freshness threshold exceeds {MAX_FRESHNESS_HOURS} hours."

    def check(self, pipeline: Any) -> LintResult:
        freshness = getattr(pipeline, "freshness", None)
        if not isinstance(freshness, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="Skipped — no freshness dict.")
        value = freshness.get("value")
        unit = freshness.get("unit", "hours")
        if value is None:
            return LintResult(rule=self.name, severity=Severity.OK, message="No freshness value to check.")
        multipliers = {"seconds": 1 / 3600, "minutes": 1 / 60, "hours": 1, "days": 24}
        hours = float(value) * multipliers.get(unit, 1)
        if hours > MAX_FRESHNESS_HOURS:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message=(
                    f"Freshness threshold of {value} {unit} ({hours:.1f}h) exceeds "
                    f"the recommended maximum of {MAX_FRESHNESS_HOURS}h."
                ),
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Freshness threshold is within limits.")
