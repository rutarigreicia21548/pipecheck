from dataclasses import dataclass
from pipecheck.rules.base import LintResult, Rule, Severity

VALID_ENCRYPTION_STANDARDS = {"AES-128", "AES-256", "RSA-2048", "RSA-4096", "ChaCha20"}
WEAK_ENCRYPTION_STANDARDS = {"DES", "3DES", "RC4", "MD5", "SHA1"}


@dataclass
class NoEncryptionRule(Rule):
    name: str = "no-encryption"
    description: str = "Pipeline should define an encryption standard"

    def check(self, pipeline) -> LintResult:
        enc = getattr(pipeline, "encryption", None)
        if not enc:
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message="No encryption standard defined; data-at-rest and in-transit may be unprotected",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Encryption standard present")


@dataclass
class WeakEncryptionRule(Rule):
    name: str = "weak-encryption"
    description: str = "Pipeline should not use weak or deprecated encryption standards"

    def check(self, pipeline) -> LintResult:
        enc = getattr(pipeline, "encryption", None)
        if not enc:
            return LintResult(rule=self.name, severity=Severity.OK, message="No encryption to validate")
        standard = enc.upper() if isinstance(enc, str) else str(enc).upper()
        for weak in WEAK_ENCRYPTION_STANDARDS:
            if weak in standard:
                return LintResult(
                    rule=self.name,
                    severity=Severity.ERROR,
                    message=f"Weak or deprecated encryption standard detected: '{enc}'",
                )
        return LintResult(rule=self.name, severity=Severity.OK, message="Encryption standard is not weak")


@dataclass
class UnrecognizedEncryptionRule(Rule):
    name: str = "unrecognized-encryption"
    description: str = "Pipeline encryption standard should be a recognized algorithm"

    def check(self, pipeline) -> LintResult:
        enc = getattr(pipeline, "encryption", None)
        if not enc:
            return LintResult(rule=self.name, severity=Severity.OK, message="No encryption to validate")
        standard = enc.upper() if isinstance(enc, str) else str(enc).upper()
        if not any(v in standard for v in VALID_ENCRYPTION_STANDARDS):
            return LintResult(
                rule=self.name,
                severity=Severity.WARNING,
                message=f"Unrecognized encryption standard: '{enc}'; expected one of {sorted(VALID_ENCRYPTION_STANDARDS)}",
            )
        return LintResult(rule=self.name, severity=Severity.OK, message="Encryption standard is recognized")
