from dataclasses import dataclass
from pipecheck.rules.base import Rule, LintResult, Severity

MAX_MEMORY_MB = 16384
MAX_CPU_CORES = 32


@dataclass
class NoMemoryLimitRule(Rule):
    name: str = "no_memory_limit"
    description: str = "Pipeline should define a memory limit"

    def check(self, pipeline) -> LintResult:
        if not getattr(pipeline, "memory_limit", None):
            return LintResult(rule=self.name, severity=Severity.WARNING,
                              message="No memory limit defined for pipeline")
        return LintResult(rule=self.name, severity=Severity.OK,
                          message="Memory limit is set")


@dataclass
class MemoryLimitTooHighRule(Rule):
    name: str = "memory_limit_too_high"
    description: str = f"Memory limit should not exceed {MAX_MEMORY_MB} MB"

    def check(self, pipeline) -> LintResult:
        limit = getattr(pipeline, "memory_limit", None)
        if limit is not None and limit > MAX_MEMORY_MB:
            return LintResult(rule=self.name, severity=Severity.ERROR,
                              message=f"Memory limit {limit} MB exceeds maximum {MAX_MEMORY_MB} MB")
        return LintResult(rule=self.name, severity=Severity.OK,
                          message="Memory limit within bounds")


@dataclass
class NoCPULimitRule(Rule):
    name: str = "no_cpu_limit"
    description: str = "Pipeline should define a CPU limit"

    def check(self, pipeline) -> LintResult:
        if not getattr(pipeline, "cpu_limit", None):
            return LintResult(rule=self.name, severity=Severity.WARNING,
                              message="No CPU limit defined for pipeline")
        return LintResult(rule=self.name, severity=Severity.OK,
                          message="CPU limit is set")


@dataclass
class CPULimitTooHighRule(Rule):
    name: str = "cpu_limit_too_high"
    description: str = f"CPU limit should not exceed {MAX_CPU_CORES} cores"

    def check(self, pipeline) -> LintResult:
        limit = getattr(pipeline, "cpu_limit", None)
        if limit is not None and limit > MAX_CPU_CORES:
            return LintResult(rule=self.name, severity=Severity.ERROR,
                              message=f"CPU limit {limit} cores exceeds maximum {MAX_CPU_CORES} cores")
        return LintResult(rule=self.name, severity=Severity.OK,
                          message="CPU limit within bounds")


DEFAULT_RESOURCE_RULES = [
    NoMemoryLimitRule(),
    MemoryLimitTooHighRule(),
    NoCPULimitRule(),
    CPULimitTooHighRule(),
]
