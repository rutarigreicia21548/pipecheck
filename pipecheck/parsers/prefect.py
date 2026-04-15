"""Parser for Prefect flow configuration files."""

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class PrefectParseError(Exception):
    """Raised when a Prefect flow file cannot be parsed."""


@dataclass
class PrefectFlow:
    """Represents a parsed Prefect flow definition."""

    name: str
    schedule: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    source_file: Optional[str] = None


def _keyword_value(keywords: list, key: str) -> Optional[ast.expr]:
    """Return the AST node for a given keyword argument name."""
    for kw in keywords:
        if kw.arg == key:
            return kw.value
    return None


def _extract_string(node: Optional[ast.expr]) -> Optional[str]:
    """Safely extract a string constant from an AST node."""
    if node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _extract_tags(node: Optional[ast.expr]) -> List[str]:
    """Extract a list of string tags from an AST List node."""
    if node is None or not isinstance(node, ast.List):
        return []
    return [
        elt.value
        for elt in node.elts
        if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
    ]


def _extract_flow_calls(tree: ast.Module) -> List[PrefectFlow]:
    """Walk the AST and collect all @flow decorated function definitions."""
    flows: List[PrefectFlow] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue

        for decorator in node.decorator_list:
            is_flow_decorator = False
            keywords: list = []

            if isinstance(decorator, ast.Name) and decorator.id == "flow":
                is_flow_decorator = True
            elif (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Name)
                and decorator.func.id == "flow"
            ):
                is_flow_decorator = True
                keywords = decorator.keywords

            if not is_flow_decorator:
                continue

            name_node = _keyword_value(keywords, "name")
            flow_name = _extract_string(name_node) or node.name

            schedule_node = _keyword_value(keywords, "schedule")
            schedule = _extract_string(schedule_node)

            description_node = _keyword_value(keywords, "description")
            description = _extract_string(description_node)

            tags_node = _keyword_value(keywords, "tags")
            tags = _extract_tags(tags_node)

            flows.append(
                PrefectFlow(
                    name=flow_name,
                    schedule=schedule,
                    description=description,
                    tags=tags,
                )
            )

    return flows


def parse_prefect_file(path: str) -> List[PrefectFlow]:
    """Parse a Prefect flow file and return all discovered flow definitions.

    Args:
        path: Path to the Python source file containing Prefect flow definitions.

    Returns:
        A list of :class:`PrefectFlow` instances found in the file.

    Raises:
        PrefectParseError: If the file cannot be read or contains invalid syntax.
    """
    source_path = Path(path)
    try:
        source = source_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PrefectParseError(f"Cannot read file '{path}': {exc}") from exc

    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as exc:
        raise PrefectParseError(
            f"Syntax error in '{path}' at line {exc.lineno}: {exc.msg}"
        ) from exc

    flows = _extract_flow_calls(tree)
    for flow in flows:
        flow.source_file = path
    return flows
