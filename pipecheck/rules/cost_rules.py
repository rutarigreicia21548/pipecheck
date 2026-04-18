from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity

MAX_COST_LIMIT = 1000.0
WARN_COST_LIMIT = 500.0
VALID_COST_TIERS = {"low", "medium", "high", "critical"}


@dataclass
class NoCostEstimateRule(Rule):
    name: str = "no_cost_estimate"
    description: str = "Pipeline should define a cost estimate or tier"

    def check(self, pipeline) -> LintResult:
        cost = getattr(pipeline, "cost_estimate", None)
        tier = getattr(pipeline, "cost_tier", None)
        if not cost and not tier:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="No cost estimate or cost tier defined",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")


@dataclass
class CostEstimateTooHighRule(Rule):
    name: str = "cost_estimate_too_high"
    description: str = f"Cost estimate should not exceed {MAX_COST_LIMIT}"

    def check(self, pipeline) -> LintResult:
        cost = getattr(pipeline, "cost_estimate", None)
        if cost is None:
            return LintResult(rule=self.name, severity=Severity.OK, message="OK")
        try:
            value = float(cost)
        except (TypeError, ValueError):
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"cost_estimate must be a number, got: {cost!r}",
            )
        if value > MAX_COST_LIMIT:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"cost_estimate {value} exceeds maximum {MAX_COST_LIMIT}",
            )
        if value > WARN_COST_LIMIT:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message=f"cost_estimate {value} is high (>{WARN_COST_LIMIT}), consider reviewing",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")


@dataclass
class InvalidCostTierRule(Rule):
    name: str = "invalid_cost_tier"
    description: str = f"cost_tier must be one of {sorted(VALID_COST_TIERS)}"

    def check(self, pipeline) -> LintResult:
        tier = getattr(pipeline, "cost_tier", None)
        if not tier:
            return LintResult(rule=self.name, severity=Severity.OK, message="OK")
        if tier not in VALID_COST_TIERS:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"cost_tier {tier!r} is invalid; must be one of {sorted(VALID_COST_TIERS)}",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")
