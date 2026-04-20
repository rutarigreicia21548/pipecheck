from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity

VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
MAX_LOG_RETENTION_DAYS = 365


@dataclass
class NoLoggingConfigRule(Rule):
    name: str = "no-logging-config"
    description: str = "Pipeline should define a logging configuration"

    def check(self, pipeline) -> LintResult:
        log_config = getattr(pipeline, "log_config", None)
        if not log_config:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="No logging configuration defined; consider adding log_config",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")


@dataclass
class InvalidLogLevelRule(Rule):
    name: str = "invalid-log-level"
    description: str = "Log level must be a recognised severity string"

    def check(self, pipeline) -> LintResult:
        log_config = getattr(pipeline, "log_config", None)
        if not isinstance(log_config, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="OK")
        level = log_config.get("level")
        if level is None:
            return LintResult(rule=self.name, severity=Severity.OK, message="OK")
        if str(level).upper() not in VALID_LOG_LEVELS:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Invalid log level '{level}'; must be one of {sorted(VALID_LOG_LEVELS)}",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")


@dataclass
class LogRetentionTooLongRule(Rule):
    name: str = "log-retention-too-long"
    description: str = f"Log retention must not exceed {MAX_LOG_RETENTION_DAYS} days"

    def check(self, pipeline) -> LintResult:
        log_config = getattr(pipeline, "log_config", None)
        if not isinstance(log_config, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="OK")
        retention = log_config.get("retention_days")
        if retention is None:
            return LintResult(rule=self.name, severity=Severity.OK, message="OK")
        try:
            retention = int(retention)
        except (TypeError, ValueError):
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"log_config.retention_days must be an integer, got '{retention}'",
            )
        if retention > MAX_LOG_RETENTION_DAYS:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=(
                    f"Log retention {retention} days exceeds maximum "
                    f"of {MAX_LOG_RETENTION_DAYS} days"
                ),
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")
