from dataclasses import dataclass, field
from pipecheck.rules.base import Severity
from pipecheck.rules.encryption_rules import (
    NoEncryptionRule,
    WeakEncryptionRule,
    UnrecognizedEncryptionRule,
)


@dataclass
class _FullPipeline:
    id: str = "my_pipeline"
    encryption: object = None


def _encryption_rules():
    return [NoEncryptionRule(), WeakEncryptionRule(), UnrecognizedEncryptionRule()]


def test_valid_encryption_all_pass():
    pipeline = _FullPipeline(encryption="AES-256")
    results = [r.check(pipeline) for r in _encryption_rules()]
    assert all(r.severity == Severity.OK for r in results)


def test_missing_encryption_produces_warning():
    pipeline = _FullPipeline(encryption=None)
    results = [r.check(pipeline) for r in _encryption_rules()]
    warnings = [r for r in results if r.severity == Severity.WARNING]
    assert len(warnings) >= 1


def test_weak_encryption_produces_error():
    pipeline = _FullPipeline(encryption="DES")
    results = [r.check(pipeline) for r in _encryption_rules()]
    errors = [r for r in results if r.severity == Severity.ERROR]
    assert len(errors) >= 1


def test_unrecognized_encryption_produces_warning():
    pipeline = _FullPipeline(encryption="BLOWFISH")
    results = [r.check(pipeline) for r in _encryption_rules()]
    warnings = [r for r in results if r.severity == Severity.WARNING]
    assert len(warnings) >= 1


def test_weak_encryption_flagged_before_unrecognized():
    """Weak algorithms like MD5 should trigger error, not just a warning."""
    pipeline = _FullPipeline(encryption="MD5")
    weak_result = WeakEncryptionRule().check(pipeline)
    assert weak_result.severity == Severity.ERROR
