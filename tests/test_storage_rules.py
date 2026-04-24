import pytest
from dataclasses import dataclass, field
from typing import Any

from pipecheck.rules.base import Severity
from pipecheck.rules.storage_rules import (
    NoStorageConfigRule,
    InvalidStorageBackendRule,
    InvalidStorageClassRule,
    RetentionTooLongRule,
)


@dataclass
class _FakePipeline:
    storage: Any = None


# ---------------------------------------------------------------------------
# NoStorageConfigRule
# ---------------------------------------------------------------------------

def test_no_storage_returns_warning():
    result = NoStorageConfigRule().check(_FakePipeline())
    assert result.severity == Severity.WARNING


def test_empty_dict_storage_returns_warning():
    result = NoStorageConfigRule().check(_FakePipeline(storage={}))
    assert result.severity == Severity.WARNING


def test_storage_present_passes_no_storage_rule():
    result = NoStorageConfigRule().check(_FakePipeline(storage={"backend": "s3"}))
    assert result.severity == Severity.OK


def test_storage_string_passes_no_storage_rule():
    result = NoStorageConfigRule().check(_FakePipeline(storage="s3"))
    assert result.severity == Severity.OK


# ---------------------------------------------------------------------------
# InvalidStorageBackendRule
# ---------------------------------------------------------------------------

def test_no_storage_dict_passes_backend_rule():
    result = InvalidStorageBackendRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_valid_backends_pass():
    for backend in ("s3", "gcs", "azure_blob", "local", "hdfs"):
        result = InvalidStorageBackendRule().check(
            _FakePipeline(storage={"backend": backend})
        )
        assert result.severity == Severity.OK, f"Expected OK for backend '{backend}'"


def test_invalid_backend_returns_error():
    result = InvalidStorageBackendRule().check(
        _FakePipeline(storage={"backend": "dropbox"})
    )
    assert result.severity == Severity.ERROR
    assert "dropbox" in result.message


def test_missing_backend_key_passes_backend_rule():
    result = InvalidStorageBackendRule().check(_FakePipeline(storage={"class": "standard"}))
    assert result.severity == Severity.OK


# ---------------------------------------------------------------------------
# InvalidStorageClassRule
# ---------------------------------------------------------------------------

def test_no_storage_dict_passes_class_rule():
    result = InvalidStorageClassRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_valid_storage_classes_pass():
    for cls in ("standard", "nearline", "coldline", "archive", "infrequent_access"):
        result = InvalidStorageClassRule().check(
            _FakePipeline(storage={"class": cls})
        )
        assert result.severity == Severity.OK, f"Expected OK for class '{cls}'"


def test_invalid_storage_class_returns_warning():
    result = InvalidStorageClassRule().check(
        _FakePipeline(storage={"class": "ultra_fast"})
    )
    assert result.severity == Severity.WARNING
    assert "ultra_fast" in result.message


# ---------------------------------------------------------------------------
# RetentionTooLongRule
# ---------------------------------------------------------------------------

def test_no_storage_dict_passes_retention_rule():
    result = RetentionTooLongRule().check(_FakePipeline())
    assert result.severity == Severity.OK


def test_no_retention_key_passes_retention_rule():
    result = RetentionTooLongRule().check(_FakePipeline(storage={"backend": "s3"}))
    assert result.severity == Severity.OK


def test_retention_within_limit_passes():
    result = RetentionTooLongRule().check(
        _FakePipeline(storage={"retention_days": 365})
    )
    assert result.severity == Severity.OK


def test_retention_at_limit_passes():
    result = RetentionTooLongRule().check(
        _FakePipeline(storage={"retention_days": 3650})
    )
    assert result.severity == Severity.OK


def test_retention_too_long_returns_error():
    result = RetentionTooLongRule().check(
        _FakePipeline(storage={"retention_days": 9999})
    )
    assert result.severity == Severity.ERROR
    assert "9999" in result.message
