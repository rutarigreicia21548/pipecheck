import pytest
from dataclasses import dataclass, field
from typing import Optional
from pipecheck.rules.base import Severity
from pipecheck.rules.version_rules import (
    NoVersionRule,
    InvalidVersionFormatRule,
    MajorVersionZeroRule,
)


@dataclass
class _FakePipeline:
    version: Optional[str] = None


# NoVersionRule

def test_no_version_returns_warning():
    r = NoVersionRule().check(_FakePipeline(version=None))
    assert r.severity == Severity.WARNING

def test_empty_version_returns_warning():
    r = NoVersionRule().check(_FakePipeline(version=""))
    assert r.severity == Severity.WARNING

def test_version_present_passes_no_version_rule():
    r = NoVersionRule().check(_FakePipeline(version="1.2.3"))
    assert r.severity == Severity.OK


# InvalidVersionFormatRule

def test_valid_semver_passes():
    r = InvalidVersionFormatRule().check(_FakePipeline(version="2.10.0"))
    assert r.severity == Severity.OK

def test_invalid_version_format_returns_error():
    r = InvalidVersionFormatRule().check(_FakePipeline(version="v1.0"))
    assert r.severity == Severity.ERROR

def test_version_with_suffix_returns_error():
    r = InvalidVersionFormatRule().check(_FakePipeline(version="1.0.0-beta"))
    assert r.severity == Severity.ERROR

def test_no_version_skips_format_check():
    r = InvalidVersionFormatRule().check(_FakePipeline(version=None))
    assert r.severity == Severity.OK


# MajorVersionZeroRule

def test_major_version_zero_returns_warning():
    r = MajorVersionZeroRule().check(_FakePipeline(version="0.3.1"))
    assert r.severity == Severity.WARNING

def test_major_version_nonzero_passes():
    r = MajorVersionZeroRule().check(_FakePipeline(version="1.0.0"))
    assert r.severity == Severity.OK

def test_no_version_skips_major_version_check():
    r = MajorVersionZeroRule().check(_FakePipeline(version=None))
    assert r.severity == Severity.OK
