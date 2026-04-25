from __future__ import annotations
from dataclasses import dataclass
from pipecheck.rules.base import LintResult, Rule, Severity

VALID_NETWORK_MODES = {"vpc", "public", "private", "isolated", "peered"}
MAX_ALLOWED_PORTS = 10


@dataclass
class NoNetworkConfigRule(Rule):
    name: str = "no-network-config"
    description: str = "Pipeline should define a network configuration."

    def check(self, pipeline) -> LintResult:
        val = getattr(pipeline, "network", None)
        if not val:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="No network configuration defined.",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")


@dataclass
class InvalidNetworkModeRule(Rule):
    name: str = "invalid-network-mode"
    description: str = "Network mode must be one of the recognised values."

    def check(self, pipeline) -> LintResult:
        network = getattr(pipeline, "network", None)
        if not isinstance(network, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="OK")
        mode = network.get("mode")
        if mode is None:
            return LintResult(rule=self.name, severity=Severity.OK, message="OK")
        if mode not in VALID_NETWORK_MODES:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Invalid network mode '{mode}'. Must be one of: {sorted(VALID_NETWORK_MODES)}.",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")


@dataclass
class TooManyOpenPortsRule(Rule):
    name: str = "too-many-open-ports"
    description: str = f"Pipeline should not expose more than {MAX_ALLOWED_PORTS} ports."

    def check(self, pipeline) -> LintResult:
        network = getattr(pipeline, "network", None)
        if not isinstance(network, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="OK")
        ports = network.get("ports", [])
        if not isinstance(ports, (list, tuple)):
            return LintResult(rule=self.name, severity=Severity.OK, message="OK")
        if len(ports) > MAX_ALLOWED_PORTS:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message=f"Too many open ports ({len(ports)}). Maximum allowed is {MAX_ALLOWED_PORTS}.",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")


@dataclass
class PublicNetworkWithoutEncryptionRule(Rule):
    name: str = "public-network-without-encryption"
    description: str = "Pipelines on a public network must define encryption."

    def check(self, pipeline) -> LintResult:
        network = getattr(pipeline, "network", None)
        if not isinstance(network, dict):
            return LintResult(rule=self.name, severity=Severity.OK, message="OK")
        if network.get("mode") != "public":
            return LintResult(rule=self.name, severity=Severity.OK, message="OK")
        encryption = getattr(pipeline, "encryption", None)
        if not encryption:
            return LintResult(
                rule=self.name,
                severity=Severity.ERROR,
                message="Pipeline uses a public network but has no encryption configured.",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="OK")
