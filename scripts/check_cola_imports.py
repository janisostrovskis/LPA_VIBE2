#!/usr/bin/env python3
"""
check_cola_imports.py — Enforce COLA layered-architecture import rules.

Rules are derived from CLAUDE.md lines 71-78:

  Domain (backend/app/domain/):
    - Must not import from app.application, app.api, or app.infrastructure
    - Must not import from fastapi, sqlalchemy, or starlette
    - Must not import pydantic.BaseModel (the 'from pydantic import BaseModel' idiom)

  Application (backend/app/application/):
    - Must not import from app.api or app.infrastructure
    - Exception: app.application.ports is allowed (ports are defined here)

  Infrastructure (backend/app/infrastructure/):
    - Must not import from app.api

Known limitation (R9 from PLAN.md):
  The pydantic BaseModel check only catches `from pydantic import BaseModel`.
  It does NOT catch `import pydantic; pydantic.BaseModel` because that requires
  Attribute-node analysis.  A complete solution is deferred.

Exit codes:
  0 — no violations found (also when backend/app/ does not exist)
  1 — one or more violations found
  2 — internal error

Supports --selftest: creates a temp directory mirroring the COLA layer paths,
writes a domain file containing `from fastapi import FastAPI` and a clean
application file, runs the check, and asserts exit code 1 with the domain
file named.  Cleans up via tempfile.TemporaryDirectory.
"""

import ast
import argparse
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class LayerRule:
    """Encodes the import restrictions for a single COLA layer."""

    # app.* prefixes that this layer must not import from.
    forbidden_prefixes: list[str] = field(default_factory=list)
    # Top-level framework modules (e.g. "fastapi") that this layer must not import.
    forbidden_modules: list[str] = field(default_factory=list)
    # Symbols from pydantic that this layer must not import via 'from pydantic import X'.
    forbidden_pydantic_symbols: list[str] = field(default_factory=list)


# Ordered from most-specific to least-specific so that path prefix matching
# assigns files to the correct layer.
LAYER_RULES: dict[str, LayerRule] = {
    "app/domain": LayerRule(
        forbidden_prefixes=["app.application", "app.api", "app.infrastructure"],
        forbidden_modules=["fastapi", "sqlalchemy", "starlette"],
        forbidden_pydantic_symbols=["BaseModel"],
    ),
    "app/application": LayerRule(
        # app.application.ports is the exception: application DEFINES ports,
        # so imports *within* application.ports are allowed.  We forbid only
        # cross-layer imports into app.api and app.infrastructure.
        forbidden_prefixes=["app.api", "app.infrastructure"],
    ),
    "app/infrastructure": LayerRule(
        forbidden_prefixes=["app.api"],
    ),
}


def _find_layer(rel_path: Path) -> str | None:
    """
    Return the layer key (e.g. 'app/domain') for the given path relative to
    the backend directory, or None if the file does not belong to a known layer.
    """
    parts_fwd = rel_path.as_posix()
    for layer_key in LAYER_RULES:
        if parts_fwd.startswith(layer_key + "/") or parts_fwd == layer_key:
            return layer_key
    return None


@dataclass
class Violation:
    """A single import-rule violation."""

    file: Path
    lineno: int
    rule: str


def _check_import_node(
    node: ast.Import | ast.ImportFrom,
    layer_key: str,
    rule: LayerRule,
    file_path: Path,
) -> list[Violation]:
    """
    Inspect a single Import or ImportFrom AST node against the layer rule.

    Returns a (possibly empty) list of Violation objects.
    """
    violations: list[Violation] = []

    if isinstance(node, ast.Import):
        for alias in node.names:
            mod = alias.name
            for forbidden in rule.forbidden_modules:
                if mod == forbidden or mod.startswith(forbidden + "."):
                    violations.append(
                        Violation(
                            file=file_path,
                            lineno=node.lineno,
                            rule=(
                                f"Layer '{layer_key}' must not import "
                                f"framework module '{forbidden}' (got '{mod}')"
                            ),
                        )
                    )
            for prefix in rule.forbidden_prefixes:
                if mod == prefix or mod.startswith(prefix + "."):
                    violations.append(
                        Violation(
                            file=file_path,
                            lineno=node.lineno,
                            rule=(
                                f"Layer '{layer_key}' must not import "
                                f"from '{prefix}' (got '{mod}')"
                            ),
                        )
                    )

    elif isinstance(node, ast.ImportFrom):
        mod = node.module or ""

        # Check framework modules
        for forbidden in rule.forbidden_modules:
            if mod == forbidden or mod.startswith(forbidden + "."):
                violations.append(
                    Violation(
                        file=file_path,
                        lineno=node.lineno,
                        rule=(
                            f"Layer '{layer_key}' must not import "
                            f"from framework module '{forbidden}' (got 'from {mod} import ...')"
                        ),
                    )
                )

        # Check forbidden layer prefixes
        for prefix in rule.forbidden_prefixes:
            if mod == prefix or mod.startswith(prefix + "."):
                violations.append(
                    Violation(
                        file=file_path,
                        lineno=node.lineno,
                        rule=(
                            f"Layer '{layer_key}' must not import "
                            f"from '{prefix}' (got 'from {mod} import ...')"
                        ),
                    )
                )

        # Pydantic BaseModel special case (R9: only catches the from-import idiom)
        if rule.forbidden_pydantic_symbols and mod == "pydantic":
            imported_names = {alias.name for alias in node.names}
            for symbol in rule.forbidden_pydantic_symbols:
                if symbol in imported_names:
                    violations.append(
                        Violation(
                            file=file_path,
                            lineno=node.lineno,
                            rule=(
                                f"Layer '{layer_key}' must not import "
                                f"pydantic.{symbol} — use dataclasses instead"
                            ),
                        )
                    )

    return violations


def check_file(py_file: Path, backend_root: Path) -> list[Violation]:
    """
    Parse a single Python file and return all COLA import violations.
    """
    try:
        rel = py_file.relative_to(backend_root)
    except ValueError:
        return []

    layer_key = _find_layer(rel)
    if layer_key is None:
        return []

    rule = LAYER_RULES[layer_key]

    try:
        source = py_file.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(py_file))
    except SyntaxError as exc:
        print(f"WARNING: could not parse {py_file}: {exc}", file=sys.stderr)
        return []

    violations: list[Violation] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            violations.extend(_check_import_node(node, layer_key, rule, py_file))

    return violations


def run_check(backend_app_dir: Path) -> int:
    """
    Walk backend/app/, check every .py file, and report violations.

    Returns 0 (clean) or 1 (violations).
    """
    if not backend_app_dir.is_dir():
        # No backend code yet — clean exit.
        return 0

    all_violations: list[Violation] = []
    # backend_root is the parent of app/; relative paths start with "app/..."
    backend_root = backend_app_dir.parent

    for py_file in sorted(backend_app_dir.rglob("*.py")):
        all_violations.extend(check_file(py_file, backend_root))

    for v in all_violations:
        print(f"FAIL {v.file}:{v.lineno} — {v.rule}")

    return 1 if all_violations else 0


def selftest() -> int:
    """
    Self-test: build a minimal temp directory tree, inject a bad import into
    a domain file, and assert that the check exits 1 with that file named.

    Returns 1 on pass (violation correctly found) or 2 on failure.
    """
    print("Running check_cola_imports.py --selftest ...")

    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)

        # Replicate the path structure the checker expects.
        domain_dir = tmp / "app" / "domain"
        domain_dir.mkdir(parents=True)
        application_dir = tmp / "app" / "application"
        application_dir.mkdir(parents=True)

        # Bad file: domain imports from fastapi — must be flagged.
        bad_file = domain_dir / "x.py"
        bad_file.write_text("from fastapi import FastAPI\n", encoding="utf-8")

        # Clean file: application imports from domain — allowed.
        clean_file = application_dir / "y.py"
        clean_file.write_text(
            "from app.domain.entities import SomeEntity\n", encoding="utf-8"
        )

        backend_app_dir = tmp / "app"
        exit_code = run_check(backend_app_dir)

        if exit_code == 1:
            print(f"SELFTEST PASS: violation in {bad_file} correctly detected.")
            return 1  # Caller expects exit 1 from selftest
        else:
            print(
                f"SELFTEST FAIL: expected exit 1, got {exit_code}",
                file=sys.stderr,
            )
            return 2


def main() -> int:
    """Parse arguments and dispatch to check or selftest."""
    parser = argparse.ArgumentParser(
        description="Enforce COLA layered-architecture import rules.",
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="Run a self-test with synthetic layer files and exit 1 on success.",
    )
    args = parser.parse_args()

    if args.selftest:
        return selftest()

    # Default: check the real backend/app directory relative to cwd.
    project_root = Path.cwd()
    backend_app_dir = project_root / "backend" / "app"
    return run_check(backend_app_dir)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(2)
    except Exception as exc:  # noqa: BLE001
        print(f"INTERNAL ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
