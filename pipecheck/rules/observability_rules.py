from dataclasses import dataclass
from pipecheck.rules.base import LintResult, Rule, Severity

VALID_TRACING_BACKENDS = {"opentelemetry", "datadog", "jaeger", "zipkin", "honeycomb"}
VALID_METRICS_BACKENDS = {"prometheus", "datadog", "statsd", "cloudwatch", "grafana"}
MAX_CUSTOM_METRICS = 20


@dataclass
class NoObservabilityConfigRule(Rule):
    name: str = "no_observability_config"
    description: str = "Pipeline should define an observability configuration"
    severity: Severity = Severity.WARNING

    def check(self, pipeline) -> LintResult:
        obs = getattr(pipeline, "observability", None)
        if not obs:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message="No observability config defined; consider adding tracing and metrics.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)


@dataclass
class InvalidTracingBackendRule(Rule):
    name: str = "invalid_tracing_backend"
    description: str = "Tracing backend must be a recognised provider"
    severity: Severity = Severity.ERROR

    def check(self, pipeline) -> LintResult:
        obs = getattr(pipeline, "observability", None) or {}
        if not isinstance(obs, dict):
            return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
        backend = obs.get("tracing_backend")
        if backend and backend.lower() not in VALID_TRACING_BACKENDS:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=f"Unknown tracing backend '{backend}'. Valid: {sorted(VALID_TRACING_BACKENDS)}",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)


@dataclass
class InvalidMetricsBackendRule(Rule):
    name: str = "invalid_metrics_backend"
    description: str = "Metrics backend must be a recognised provider"
    severity: Severity = Severity.ERROR

    def check(self, pipeline) -> LintResult:
        obs = getattr(pipeline, "observability", None) or {}
        if not isinstance(obs, dict):
            return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
        backend = obs.get("metrics_backend")
        if backend and backend.lower() not in VALID_METRICS_BACKENDS:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=f"Unknown metrics backend '{backend}'. Valid: {sorted(VALID_METRICS_BACKENDS)}",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)


@dataclass
class TooManyCustomMetricsRule(Rule):
    name: str = "too_many_custom_metrics"
    description: str = f"Pipeline should not define more than {MAX_CUSTOM_METRICS} custom metrics"
    severity: Severity = Severity.WARNING

    def check(self, pipeline) -> LintResult:
        obs = getattr(pipeline, "observability", None) or {}
        if not isinstance(obs, dict):
            return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
        metrics = obs.get("custom_metrics") or []
        if isinstance(metrics, list) and len(metrics) > MAX_CUSTOM_METRICS:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=f"{len(metrics)} custom metrics defined; limit is {MAX_CUSTOM_METRICS}.",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
