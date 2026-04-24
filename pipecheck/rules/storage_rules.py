from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pipecheck.rules.base import LintResult, Rule, Severity

_VALID_STORAGE_CLASSES = {"standard", "nearline", "coldline", "archive", "infrequent_access"}
_VALID_STORAGE_BACKENDS = {"s3", "gcs", "azure_blob", "local", "hdfs"}
_MAX_RETENTION_DAYS = 3650  # 10 years


@dataclass
class NoStorageConfigRule(Rule):
    name: str = "no_storage_config"
    description: str = "Pipeline should define a storage configuration."
    severity: Severity = Severity.WARNING

    def check(self, pipeline: Any) -> LintResult:
        storage = getattr(pipeline, "storage", None)
        if not storage:
            return LintResult(rule=self.name, severity=self.severity,
                              message="No storage configuration defined.")
        return LintResult(rule=self.name, severity=Severity.OK,
                          message="Storage configuration present.")


@dataclass
class InvalidStorageBackendRule(Rule):
    name: str = "invalid_storage_backend"
    description: str = "Storage backend must be a recognised provider."
    severity: Severity = Severity.ERROR

    def check(self, pipeline: Any) -> LintResult:
        storage = getattr(pipeline, "storage", None)
        if not isinstance(storage, dict):
            return LintResult(rule=self.name, severity=Severity.OK,
                              message="No storage dict to validate.")
        backend = storage.get("backend", "")
        if backend and backend.lower() not in _VALID_STORAGE_BACKENDS:
            return LintResult(rule=self.name, severity=self.severity,
                              message=f"Invalid storage backend '{backend}'. "
                                      f"Valid: {sorted(_VALID_STORAGE_BACKENDS)}.")
        return LintResult(rule=self.name, severity=Severity.OK,
                          message="Storage backend is valid.")


@dataclass
class InvalidStorageClassRule(Rule):
    name: str = "invalid_storage_class"
    description: str = "Storage class must be a recognised tier."
    severity: Severity = Severity.WARNING

    def check(self, pipeline: Any) -> LintResult:
        storage = getattr(pipeline, "storage", None)
        if not isinstance(storage, dict):
            return LintResult(rule=self.name, severity=Severity.OK,
                              message="No storage dict to validate.")
        cls = storage.get("class", "")
        if cls and cls.lower() not in _VALID_STORAGE_CLASSES:
            return LintResult(rule=self.name, severity=self.severity,
                              message=f"Invalid storage class '{cls}'. "
                                      f"Valid: {sorted(_VALID_STORAGE_CLASSES)}.")
        return LintResult(rule=self.name, severity=Severity.OK,
                          message="Storage class is valid.")


@dataclass
class RetentionTooLongRule(Rule):
    name: str = "retention_too_long"
    description: str = f"Storage retention must not exceed {_MAX_RETENTION_DAYS} days."
    severity: Severity = Severity.ERROR

    def check(self, pipeline: Any) -> LintResult:
        storage = getattr(pipeline, "storage", None)
        if not isinstance(storage, dict):
            return LintResult(rule=self.name, severity=Severity.OK,
                              message="No storage dict to validate.")
        retention = storage.get("retention_days")
        if retention is not None and isinstance(retention, (int, float)):
            if retention > _MAX_RETENTION_DAYS:
                return LintResult(rule=self.name, severity=self.severity,
                                  message=f"Retention {retention} days exceeds "
                                          f"maximum {_MAX_RETENTION_DAYS} days.")
        return LintResult(rule=self.name, severity=Severity.OK,
                          message="Storage retention is within limits.")
