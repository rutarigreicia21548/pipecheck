from __future__ import annotations

from pipecheck.rules.base import LintResult, Rule, Severity

_VALID_RATE_LIMIT_UNITS = {"second", "minute", "hour", "day"}
_MAX_RATE_LIMIT_REQUESTS = 10_000


class NoRateLimitRule(Rule):
    """Warn when a pipeline has no rate limit configuration."""

    name = "no-rate-limit"
    description = "Pipeline should define a rate limit to avoid overloading downstream systems."

    def check(self, pipeline) -> LintResult:
        rl = getattr(pipeline, "rate_limit", None)
        if not rl:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="No rate limit configured for this pipeline.",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Rate limit is set.")


class InvalidRateLimitUnitRule(Rule):
    """Error when the rate limit unit is not a recognised time window."""

    name = "invalid-rate-limit-unit"
    description = "Rate limit unit must be one of: second, minute, hour, day."

    def check(self, pipeline) -> LintResult:
        rl = getattr(pipeline, "rate_limit", None)
        if not isinstance(rl, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="No rate limit dict to validate.")
        unit = rl.get("unit", "")
        if unit and unit.lower() not in _VALID_RATE_LIMIT_UNITS:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Invalid rate limit unit '{unit}'. Must be one of: {sorted(_VALID_RATE_LIMIT_UNITS)}.",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Rate limit unit is valid.")


class RateLimitTooHighRule(Rule):
    """Error when the rate limit request count exceeds the allowed maximum."""

    name = "rate-limit-too-high"
    description = f"Rate limit requests must not exceed {_MAX_RATE_LIMIT_REQUESTS} per window."

    def check(self, pipeline) -> LintResult:
        rl = getattr(pipeline, "rate_limit", None)
        if not isinstance(rl, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="No rate limit dict to validate.")
        requests = rl.get("requests")
        if requests is not None and requests > _MAX_RATE_LIMIT_REQUESTS:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=(
                    f"Rate limit of {requests} requests exceeds maximum "
                    f"allowed value of {_MAX_RATE_LIMIT_REQUESTS}."
                ),
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Rate limit request count is acceptable.")


class ZeroRateLimitRule(Rule):
    """Error when the rate limit request count is set to zero."""

    name = "zero-rate-limit"
    description = "A rate limit of 0 requests makes the pipeline unable to run."

    def check(self, pipeline) -> LintResult:
        rl = getattr(pipeline, "rate_limit", None)
        if not isinstance(rl, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="No rate limit dict to validate.")
        requests = rl.get("requests")
        if requests is not None and requests == 0:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message="Rate limit requests is set to 0, which disables pipeline execution.",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Rate limit request count is non-zero.")
