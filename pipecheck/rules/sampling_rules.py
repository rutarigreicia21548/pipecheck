from __future__ import annotations

from pipecheck.rules.base import LintResult, Rule, Severity

_VALID_SAMPLING_STRATEGIES = {"random", "systematic", "stratified", "reservoir", "bernoulli"}
_MAX_SAMPLE_RATE = 1.0
_MIN_SAMPLE_RATE = 0.0
_WARN_SAMPLE_RATE = 0.5  # rates above this on production pipelines are suspicious


class NoSamplingConfigRule(Rule):
    """Warn when no sampling configuration is present."""

    name = "no-sampling-config"
    description = "Pipeline has no sampling configuration."
    severity = Severity.WARNING

    def check(self, pipeline) -> LintResult:
        sampling = getattr(pipeline, "sampling", None)
        if not sampling:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message="No sampling configuration found; consider defining a sampling strategy.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="", passed=True)


class InvalidSamplingStrategyRule(Rule):
    """Error when the sampling strategy is not a recognised value."""

    name = "invalid-sampling-strategy"
    description = "Sampling strategy must be one of the recognised values."
    severity = Severity.ERROR

    def check(self, pipeline) -> LintResult:
        sampling = getattr(pipeline, "sampling", None)
        if not isinstance(sampling, dict):
            return LintResult(rule=self.name, severity=self.severity, message="", passed=True)
        strategy = sampling.get("strategy")
        if strategy is None:
            return LintResult(rule=self.name, severity=self.severity, message="", passed=True)
        if strategy not in _VALID_SAMPLING_STRATEGIES:
            valid = ", ".join(sorted(_VALID_SAMPLING_STRATEGIES))
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=f"Invalid sampling strategy '{strategy}'. Valid strategies: {valid}.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="", passed=True)


class SamplingRateOutOfRangeRule(Rule):
    """Error when the sample_rate is outside the [0.0, 1.0] range."""

    name = "sampling-rate-out-of-range"
    description = "Sample rate must be between 0.0 and 1.0 inclusive."
    severity = Severity.ERROR

    def check(self, pipeline) -> LintResult:
        sampling = getattr(pipeline, "sampling", None)
        if not isinstance(sampling, dict):
            return LintResult(rule=self.name, severity=self.severity, message="", passed=True)
        rate = sampling.get("sample_rate")
        if rate is None:
            return LintResult(rule=self.name, severity=self.severity, message="", passed=True)
        try:
            rate = float(rate)
        except (TypeError, ValueError):
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=f"sample_rate '{rate}' is not a valid number.",
                passed=False,
            )
        if not (_MIN_SAMPLE_RATE <= rate <= _MAX_SAMPLE_RATE):
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=f"sample_rate {rate} is out of range; must be between 0.0 and 1.0.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="", passed=True)


class HighSamplingRateRule(Rule):
    """Warn when sample_rate exceeds 50 % — may indicate an unintentional config."""

    name = "high-sampling-rate"
    description = f"Sample rates above {_WARN_SAMPLE_RATE} may cause unexpected data volumes."
    severity = Severity.WARNING

    def check(self, pipeline) -> LintResult:
        sampling = getattr(pipeline, "sampling", None)
        if not isinstance(sampling, dict):
            return LintResult(rule=self.name, severity=self.severity, message="", passed=True)
        rate = sampling.get("sample_rate")
        if rate is None:
            return LintResult(rule=self.name, severity=self.severity, message="", passed=True)
        try:
            rate = float(rate)
        except (TypeError, ValueError):
            return LintResult(rule=self.name, severity=self.severity, message="", passed=True)
        if rate > _WARN_SAMPLE_RATE:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=f"sample_rate {rate} is high (> {_WARN_SAMPLE_RATE}); verify this is intentional.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="", passed=True)
