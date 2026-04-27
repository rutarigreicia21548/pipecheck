"""Command-line interface for pipecheck.

Provides the main entry point for validating and linting Airflow and Prefect
pipeline configuration files from the command line.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from pipecheck.parsers.airflow import AirflowParseError, parse_airflow_file
from pipecheck.parsers.prefect import PrefectParseError, parse_prefect_file
from pipecheck.rules import run_rules
from pipecheck.rules.base import LintResult, Severity


def _detect_format(path: Path) -> str:
    """Attempt to detect pipeline format from file content.

    Returns 'airflow', 'prefect', or raises ValueError if ambiguous.
    """
    text = path.read_text(encoding="utf-8")
    has_dag = "DAG(" in text or "from airflow" in text
    has_flow = "@flow" in text or "from prefect" in text

    if has_dag and not has_flow:
        return "airflow"
    if has_flow and not has_dag:
        return "prefect"
    if has_dag and has_flow:
        raise ValueError(
            f"Cannot determine format for '{path}': file contains both Airflow and Prefect markers."
        )
    raise ValueError(
        f"Cannot determine format for '{path}': no Airflow or Prefect markers found. "
        "Use --format to specify explicitly."
    )


def _format_result(result: LintResult, *, use_color: bool = True) -> str:
    """Format a single LintResult for terminal output."""
    icons = {
        Severity.ERROR: "\u2718",
        Severity.WARNING: "\u26a0",
        Severity.INFO: "\u2139",
    }
    colors = {
        Severity.ERROR: "\033[91m",
        Severity.WARNING: "\033[93m",
        Severity.INFO: "\033[94m",
    }
    reset = "\033[0m"

    icon = icons.get(result.severity, "?")
    label = result.severity.name.upper()
    msg = f"  {icon} [{label}] {result.rule_name}: {result.message}"

    if use_color:
        color = colors.get(result.severity, "")
        return f"{color}{msg}{reset}"
    return msg


def _check_file(
    path: Path,
    fmt: str | None,
    *,
    use_color: bool = True,
) -> int:
    """Parse and lint a single file.  Returns number of errors found."""
    resolved_fmt = fmt
    if resolved_fmt is None:
        try:
            resolved_fmt = _detect_format(path)
        except ValueError as exc:
            print(f"pipecheck: {exc}", file=sys.stderr)
            return 1

    try:
        if resolved_fmt == "airflow":
            pipelines = parse_airflow_file(path)
        else:
            pipelines = parse_prefect_file(path)
    except (AirflowParseError, PrefectParseError) as exc:
        print(f"pipecheck: parse error in '{path}': {exc}", file=sys.stderr)
        return 1

    if not pipelines:
        print(f"pipecheck: no pipelines found in '{path}'")
        return 0

    error_count = 0
    for pipeline in pipelines:
        pid = getattr(pipeline, "dag_id", None) or getattr(pipeline, "name", "<unknown>")
        results: List[LintResult] = run_rules(pipeline)
        errors = [r for r in results if r.severity == Severity.ERROR]
        warnings = [r for r in results if r.severity == Severity.WARNING]
        infos = [r for r in results if r.severity == Severity.INFO]

        status = "\033[92mOK\033[0m" if use_color else "OK"
        if errors:
            status = "\033[91mFAIL\033[0m" if use_color else "FAIL"
        elif warnings:
            status = "\033[93mWARN\033[0m" if use_color else "WARN"

        print(f"\n{path}::{pid}  [{status}]")
        for r in results:
            print(_format_result(r, use_color=use_color))

        summary_parts = []
        if errors:
            summary_parts.append(f"{len(errors)} error(s)")
        if warnings:
            summary_parts.append(f"{len(warnings)} warning(s)")
        if infos:
            summary_parts.append(f"{len(infos)} info(s)")
        if not results:
            summary_parts.append("no issues")
        print(f"  Summary: {', '.join(summary_parts)}")

        error_count += len(errors)

    return error_count


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="pipecheck",
        description="Validate and lint Airflow and Prefect pipeline configs.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Pipeline file(s) to check.",
    )
    parser.add_argument(
        "--format",
        choices=["airflow", "prefect"],
        default=None,
        dest="fmt",
        help="Force pipeline format instead of auto-detecting.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour output.",
    )
    parser.add_argument(
        "--fail-on-warnings",
        action="store_true",
        default=False,
        help="Exit with a non-zero status code if any warnings are found.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point.  Returns an exit code (0 = success)."""
    parser = build_parser()
    args = parser.parse_args(argv)

    use_color = not args.no_color and sys.stdout.isatty()
    total_errors = 0
    total_warnings = 0

    for file_arg in args.files:
        path = Path(file_arg)
        if not path.exists():
            print(f"pipecheck: file not found: '{path}'", file=sys.stderr)
            total_errors += 1
            continue

        file_errors = _check_file(path, args.fmt, use_color=use_color)
        total_errors += file_errors

    print(f"\n{'='*60}")
    if total_errors:
        msg = f"pipecheck: {total_errors} error(s) found — pipeline check FAILED."
        print(f"\033[91m{msg}\033[0m" if use_color else msg)
        return 1

    ok_msg = "pipecheck: all checks passed."
    print(f"\033[92m{ok_msg}\033[0m" if use_color else ok_msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
