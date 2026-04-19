from pipecheck.rules.base import LintResult, Rule, Severity

VALID_CACHE_STRATEGIES = {"memory", "disk", "redis", "s3", "none"}
MAX_CACHE_TTL_HOURS = 168  # 1 week


class NoCacheStrategyRule(Rule):
    id = "NO_CACHE_STRATEGY"
    description = "Pipeline should define a cache strategy."

    def check(self, pipeline) -> LintResult:
        val = getattr(pipeline, "cache_strategy", None)
        if not val or (isinstance(val, str) and not val.strip()):
            return LintResult(
                rule_id=self.id,
                severity=Severity.WARNING,
                message="No cache strategy defined; consider setting cache_strategy.",
            )
        return LintResult(rule_id=self.id, severity=Severity.OK, message="OK")


class InvalidCacheStrategyRule(Rule):
    id = "INVALID_CACHE_STRATEGY"
    description = "Cache strategy must be one of the known valid strategies."

    def check(self, pipeline) -> LintResult:
        val = getattr(pipeline, "cache_strategy", None)
        if not val:
            return LintResult(rule_id=self.id, severity=Severity.OK, message="OK")
        if isinstance(val, str) and val.strip().lower() not in VALID_CACHE_STRATEGIES:
            return LintResult(
                rule_id=self.id,
                severity=Severity.ERROR,
                message=f"Invalid cache strategy '{val}'. Must be one of {sorted(VALID_CACHE_STRATEGIES)}.",
            )
        return LintResult(rule_id=self.id, severity=Severity.OK, message="OK")


class CacheTTLTooLongRule(Rule):
    id = "CACHE_TTL_TOO_LONG"
    description = f"Cache TTL should not exceed {MAX_CACHE_TTL_HOURS} hours."

    def check(self, pipeline) -> LintResult:
        ttl = getattr(pipeline, "cache_ttl_hours", None)
        if ttl is None:
            return LintResult(rule_id=self.id, severity=Severity.OK, message="OK")
        try:
            if float(ttl) > MAX_CACHE_TTL_HOURS:
                return LintResult(
                    rule_id=self.id,
                    severity=Severity.WARNING,
                    message=f"Cache TTL {ttl}h exceeds recommended maximum of {MAX_CACHE_TTL_HOURS}h.",
                )
        except (TypeError, ValueError):
            return LintResult(
                rule_id=self.id,
                severity=Severity.ERROR,
                message=f"Cache TTL '{ttl}' is not a valid number.",
            )
        return LintResult(rule_id=self.id, severity=Severity.OK, message="OK")


class ZeroCacheTTLRule(Rule):
    id = "ZERO_CACHE_TTL"
    description = "Cache TTL of zero disables caching effectively."

    def check(self, pipeline) -> LintResult:
        ttl = getattr(pipeline, "cache_ttl_hours", None)
        if ttl is None:
            return LintResult(rule_id=self.id, severity=Severity.OK, message="OK")
        try:
            if float(ttl) == 0:
                return LintResult(
                    rule_id=self.id,
                    severity=Severity.WARNING,
                    message="Cache TTL is 0; caching will have no effect.",
                )
        except (TypeError, ValueError):
            pass
        return LintResult(rule_id=self.id, severity=Severity.OK, message="OK")
