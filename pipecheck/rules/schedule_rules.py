"""Lint rules related to pipeline scheduling."""

from __future__ import annotations

import re
from typing import Any

from pipecheck.rules.base import LintResult, Rule, Severity

# Basic cron expression pattern (5 fields)
_CRON_RE = re.compile(
    r"^(\*|[0-9,\-*/]+)\s"
    r"(\*|[0-9,\-*/]+)\s"
    r"(\*|[0-9,\-*/]+)\s"
    r"(\*|[0-9,\-*/]+)\s"
    r"(\*|[0-9,\-*/]+)$"
)

# Common Airflow/Prefect preset schedules
_PRESET_SCHEDULES = {
    "@once", "@hourly", "@daily", "@weekly", "@monthly", "@yearly", "@continuous",
}


class NoScheduleRule(Rule):
    """Warn when a pipeline has no schedule defined."""

    id = "no-schedule"
    description = "Pipeline should define a schedule."
    severity = Severity.WARNING

    def check(self, pipeline: Any) -> LintResult | None:
        schedule = getattr(pipeline, "schedule", None)
        if not schedule:
            return LintResult(
                rule_id=self.id,
                severity=self.severity,
                message=f"Pipeline '{pipeline.id or pipeline.name}' has no schedule defined.",
            )
        return None


class InvalidCronScheduleRule(Rule):
    """Error when a cron-style schedule string is malformed."""

    id = "invalid-cron"
    description = "Cron schedule expression must be valid."
    severity = Severity.ERROR

    def check(self, pipeline: Any) -> LintResult | None:
        schedule = getattr(pipeline, "schedule", None)
        if not schedule:
            return None
        if schedule in _PRESET_SCHEDULES:
            return None
        if not _CRON_RE.match(schedule.strip()):
            return LintResult(
                rule_id=self.id,
                severity=self.severity,
                message=(
                    f"Pipeline '{pipeline.id or pipeline.name}' has an invalid "
                    f"cron expression: '{schedule}'."
                ),
            )
        return None


class FrequentScheduleRule(Rule):
    """Warn when a pipeline is scheduled more often than every 5 minutes."""

    id = "too-frequent-schedule"
    description = "Pipelines should not run more often than every 5 minutes."
    severity = Severity.WARNING

    def check(self, pipeline: Any) -> LintResult | None:
        schedule = getattr(pipeline, "schedule", None)
        if not schedule or not _CRON_RE.match(str(schedule).strip()):
            return None
        minute_field = schedule.strip().split()[0]
        # Detect */N where N < 5
        match = re.fullmatch(r"\*/(\d+)", minute_field)
        if match and int(match.group(1)) < 5:
            return LintResult(
                rule_id=self.id,
                severity=self.severity,
                message=(
                    f"Pipeline '{pipeline.id or pipeline.name}' runs every "
                    f"{match.group(1)} minute(s), which may be too frequent."
                ),
            )
        return None
