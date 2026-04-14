"""Parser for Apache Airflow DAG configuration files."""

from __future__ import annotations

import ast
import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AirflowDAG:
    """Represents a parsed Airflow DAG definition."""

    dag_id: str
    schedule_interval: str | None = None
    default_args: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    catchup: bool | None = None
    source_file: str = ""


class AirflowParseError(Exception):
    """Raised when an Airflow DAG file cannot be parsed."""


def _extract_dag_calls(tree: ast.Module) -> list[ast.Call]:
    """Walk the AST and collect all DAG(...) constructor calls."""
    dag_calls: list[ast.Call] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = (
                func.id
                if isinstance(func, ast.Name)
                else getattr(func, "attr", None)
            )
            if name == "DAG":
                dag_calls.append(node)
    return dag_calls


def _keyword_value(call: ast.Call, key: str) -> ast.expr | None:
    """Return the AST expression for a keyword argument, or None."""
    for kw in call.keywords:
        if kw.arg == key:
            return kw.value
    return None


def _literal(node: ast.expr | None) -> Any:
    """Safely evaluate a constant / literal AST node."""
    if node is None:
        return None
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError):
        return None


def parse_airflow_file(path: str) -> list[AirflowDAG]:
    """Parse an Airflow Python DAG file and return all DAG definitions found.

    Args:
        path: Absolute or relative path to the ``.py`` file.

    Returns:
        A list of :class:`AirflowDAG` instances (may be empty).

    Raises:
        AirflowParseError: If the file cannot be read or is not valid Python.
    """
    if not os.path.isfile(path):
        raise AirflowParseError(f"File not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as fh:
            source = fh.read()
        tree = ast.parse(source, filename=path)
    except SyntaxError as exc:
        raise AirflowParseError(f"Syntax error in {path}: {exc}") from exc
    except OSError as exc:
        raise AirflowParseError(f"Cannot read {path}: {exc}") from exc

    dags: list[AirflowDAG] = []
    for call in _extract_dag_calls(tree):
        dag_id = _literal(_keyword_value(call, "dag_id"))
        if dag_id is None and call.args:
            dag_id = _literal(call.args[0])
        if not isinstance(dag_id, str):
            dag_id = "<unknown>"

        dags.append(
            AirflowDAG(
                dag_id=dag_id,
                schedule_interval=_literal(_keyword_value(call, "schedule_interval")),
                default_args=_literal(_keyword_value(call, "default_args")) or {},
                tags=_literal(_keyword_value(call, "tags")) or [],
                catchup=_literal(_keyword_value(call, "catchup")),
                source_file=path,
            )
        )
    return dags
