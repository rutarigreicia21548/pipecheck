from __future__ import annotations

from pipecheck.rules.base import LintResult, Rule, Severity

MAX_FAN_OUT = 10
MAX_FAN_IN = 10


class NoFanOutConfigRule(Rule):
    """Warn when a pipeline has no fan-out configuration defined."""

    name = "no-fan-out-config"
    description = "Pipeline should define a fan-out configuration."
    severity = Severity.WARNING

    def check(self, pipeline) -> LintResult:
        fan_out = getattr(pipeline, "fan_out", None)
        if not fan_out:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message="No fan-out configuration defined; consider specifying fan_out.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)


class FanOutTooHighRule(Rule):
    """Error when fan-out degree exceeds the allowed maximum."""

    name = "fan-out-too-high"
    description = f"Fan-out degree must not exceed {MAX_FAN_OUT}."
    severity = Severity.ERROR

    def check(self, pipeline) -> LintResult:
        fan_out = getattr(pipeline, "fan_out", None)
        if fan_out is None:
            return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
        degree = fan_out.get("degree") if isinstance(fan_out, dict) else None
        if degree is not None and degree > MAX_FAN_OUT:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=f"Fan-out degree {degree} exceeds maximum of {MAX_FAN_OUT}.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)


class FanInTooHighRule(Rule):
    """Error when fan-in degree exceeds the allowed maximum."""

    name = "fan-in-too-high"
    description = f"Fan-in degree must not exceed {MAX_FAN_IN}."
    severity = Severity.ERROR

    def check(self, pipeline) -> LintResult:
        fan_out = getattr(pipeline, "fan_out", None)
        if fan_out is None:
            return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
        fan_in = fan_out.get("fan_in") if isinstance(fan_out, dict) else None
        if fan_in is not None and fan_in > MAX_FAN_IN:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=f"Fan-in degree {fan_in} exceeds maximum of {MAX_FAN_IN}.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)


class InvalidFanOutStrategyRule(Rule):
    """Error when an unrecognised fan-out strategy is specified."""

    name = "invalid-fan-out-strategy"
    description = "Fan-out strategy must be one of: scatter, broadcast, partition."
    severity = Severity.ERROR

    VALID_STRATEGIES = {"scatter", "broadcast", "partition"}

    def check(self, pipeline) -> LintResult:
        fan_out = getattr(pipeline, "fan_out", None)
        if not isinstance(fan_out, dict):
            return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
        strategy = fan_out.get("strategy")
        if strategy and strategy not in self.VALID_STRATEGIES:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=(
                    f"Fan-out strategy '{strategy}' is invalid; "
                    f"must be one of {sorted(self.VALID_STRATEGIES)}."
                ),
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
