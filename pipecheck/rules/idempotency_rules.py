from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity


@dataclass
class NoIdempotencyRule(Rule):
    name: str = "no_idempotency"
    description: str = "Pipeline should declare an idempotency strategy"
    severity: Severity = Severity.WARNING

    def check(self, pipeline) -> LintResult:
        val = getattr(pipeline, "idempotency", None)
        if not val:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message="No idempotency strategy defined",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)


@dataclass
class InvalidIdempotencyStrategyRule(Rule):
    name: str = "invalid_idempotency_strategy"
    description: str = "Idempotency strategy must be a recognised value"
    severity: Severity = Severity.ERROR

    VALID = {"none", "overwrite", "skip", "upsert", "append_dedup"}

    def check(self, pipeline) -> LintResult:
        val = getattr(pipeline, "idempotency", None)
        if not val:
            return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
        strategy = val if isinstance(val, str) else val.get("strategy", "")
        if strategy.lower() not in self.VALID:
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=f"Invalid idempotency strategy '{strategy}'. Must be one of {sorted(self.VALID)}",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)


@dataclass
class IdempotencyWithoutKeyRule(Rule):
    name: str = "idempotency_without_key"
    description: str = "Upsert/append_dedup idempotency strategies require a dedup_key"
    severity: Severity = Severity.ERROR

    KEY_REQUIRED = {"upsert", "append_dedup"}

    def check(self, pipeline) -> LintResult:
        val = getattr(pipeline, "idempotency", None)
        if not val or isinstance(val, str):
            return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
        strategy = val.get("strategy", "").lower()
        if strategy in self.KEY_REQUIRED and not val.get("dedup_key"):
            return LintResult(
                rule=self.name,
                severity=self.severity,
                message=f"Strategy '{strategy}' requires a 'dedup_key' to be specified",
                passed=False,
            )
        return LintResult(rule=self.name, severity=self.severity, message="OK", passed=True)
