"""Tests for the Prefect flow parser."""

import textwrap
from pathlib import Path

import pytest

from pipecheck.parsers.prefect import (
    PrefectFlow,
    PrefectParseError,
    parse_prefect_file,
)


@pytest.fixture()
def write_flow_file(tmp_path):
    """Helper fixture that writes Python source to a temp file."""

    def _write(source: str, filename: str = "flow.py") -> str:
        p = tmp_path / filename
        p.write_text(textwrap.dedent(source))
        return str(p)

    return _write


def test_parse_simple_flow(write_flow_file):
    path = write_flow_file("""
        from prefect import flow

        @flow
        def my_pipeline():
            pass
    """)
    flows = parse_prefect_file(path)
    assert len(flows) == 1
    assert flows[0].name == "my_pipeline"


def test_flow_with_name_kwarg(write_flow_file):
    path = write_flow_file("""
        from prefect import flow

        @flow(name="custom-name")
        def my_pipeline():
            pass
    """)
    flows = parse_prefect_file(path)
    assert flows[0].name == "custom-name"


def test_flow_with_schedule_and_description(write_flow_file):
    path = write_flow_file("""
        from prefect import flow

        @flow(name="etl", schedule="0 * * * *", description="Hourly ETL job")
        def etl_flow():
            pass
    """)
    flows = parse_prefect_file(path)
    assert flows[0].schedule == "0 * * * *"
    assert flows[0].description == "Hourly ETL job"


def test_flow_with_tags(write_flow_file):
    path = write_flow_file("""
        from prefect import flow

        @flow(tags=["prod", "etl"])
        def tagged_flow():
            pass
    """)
    flows = parse_prefect_file(path)
    assert flows[0].tags == ["prod", "etl"]


def test_multiple_flows(write_flow_file):
    path = write_flow_file("""
        from prefect import flow

        @flow
        def flow_a():
            pass

        @flow(name="flow-b")
        def flow_b():
            pass
    """)
    flows = parse_prefect_file(path)
    assert len(flows) == 2
    names = {f.name for f in flows}
    assert names == {"flow_a", "flow-b"}


def test_no_flows_returns_empty_list(write_flow_file):
    path = write_flow_file("""
        def plain_function():
            pass
    """)
    assert parse_prefect_file(path) == []


def test_source_file_is_recorded(write_flow_file):
    path = write_flow_file("""
        from prefect import flow

        @flow
        def my_flow():
            pass
    """)
    flows = parse_prefect_file(path)
    assert flows[0].source_file == path


def test_syntax_error_raises_parse_error(write_flow_file):
    path = write_flow_file("def broken(: pass")
    with pytest.raises(PrefectParseError, match="Syntax error"):
        parse_prefect_file(path)
