"""Tests for pipecheck.parsers.airflow."""

from __future__ import annotations

import textwrap
import os
import pytest

from pipecheck.parsers.airflow import AirflowDAG, AirflowParseError, parse_airflow_file


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def write_dag_file(tmp_path, content: str) -> str:
    p = tmp_path / "dag.py"
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return str(p)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_parse_simple_dag(tmp_path):
    path = write_dag_file(tmp_path, """
        from airflow import DAG
        dag = DAG(
            dag_id="my_pipeline",
            schedule_interval="@daily",
            catchup=False,
            tags=["etl", "finance"],
        )
    """)
    dags = parse_airflow_file(path)
    assert len(dags) == 1
    d = dags[0]
    assert isinstance(d, AirflowDAG)
    assert d.dag_id == "my_pipeline"
    assert d.schedule_interval == "@daily"
    assert d.catchup is False
    assert d.tags == ["etl", "finance"]
    assert d.source_file == path


def test_parse_multiple_dags(tmp_path):
    path = write_dag_file(tmp_path, """
        from airflow import DAG
        dag1 = DAG(dag_id="pipeline_a", schedule_interval=None)
        dag2 = DAG(dag_id="pipeline_b", schedule_interval="0 6 * * *")
    """)
    dags = parse_airflow_file(path)
    assert len(dags) == 2
    ids = {d.dag_id for d in dags}
    assert ids == {"pipeline_a", "pipeline_b"}


def test_dag_id_positional_argument(tmp_path):
    path = write_dag_file(tmp_path, """
        from airflow import DAG
        dag = DAG("positional_id", schedule_interval="@weekly")
    """)
    dags = parse_airflow_file(path)
    assert dags[0].dag_id == "positional_id"


def test_no_dags_returns_empty_list(tmp_path):
    path = write_dag_file(tmp_path, """
        x = 1 + 1
        print(x)
    """)
    assert parse_airflow_file(path) == []


def test_file_not_found_raises():
    with pytest.raises(AirflowParseError, match="File not found"):
        parse_airflow_file("/nonexistent/path/dag.py")


def test_syntax_error_raises(tmp_path):
    bad = tmp_path / "bad.py"
    bad.write_text("def broken(:\n    pass", encoding="utf-8")
    with pytest.raises(AirflowParseError, match="Syntax error"):
        parse_airflow_file(str(bad))


def test_default_args_parsed(tmp_path):
    path = write_dag_file(tmp_path, """
        from airflow import DAG
        args = {"owner": "alice", "retries": 3}
        dag = DAG(dag_id="with_defaults", default_args=args)
    """)
    # default_args is a variable reference — literal_eval won't resolve it
    dags = parse_airflow_file(path)
    assert dags[0].default_args == {}  # graceful fallback
