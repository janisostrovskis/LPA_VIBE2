#!/usr/bin/env python3
"""
scope_matcher.py — Shared path-matching helper for scope.yaml enforcement.

Public API:
  load_manifest(repo_root)          -> dict
  agent_allows(manifest, agent, rel_path) -> bool
  matching_glob(manifest, agent, rel_path) -> str | None

Used by:
  scripts/hooks/pretool_scope_guard.py
  scripts/preflight_dispatch.py
"""

import fnmatch
from pathlib import Path, PurePosixPath


def _parse_yaml_minimal(text: str) -> dict:
    """
    Tiny YAML subset parser for scope.yaml.
    Supports: mapping keys, string values, lists with '- ' items, comments (#),
    and multi-level indentation.  Does not support anchors, tags, or multi-line
    scalars.

    Copied verbatim from scripts/hooks/pretool_scope_guard.py.
    # TODO: dedupe with pretool_scope_guard.py once pretool_scope_guard imports
    # from this module instead of carrying its own copy.
    """
    lines = text.splitlines()
    tokens: list[tuple[int, str]] = []
    for line in lines:
        stripped = line.rstrip()
        if not stripped or stripped.lstrip().startswith("#"):
            continue
        indent = len(stripped) - len(stripped.lstrip())
        content = stripped.lstrip()
        if " #" in content:
            content = content[: content.index(" #")].rstrip()
        tokens.append((indent, content))

    def parse_value(v: str) -> str:
        v = v.strip()
        if (v.startswith('"') and v.endswith('"')) or (
            v.startswith("'") and v.endswith("'")
        ):
            return v[1:-1]
        return v

    def parse_block(start: int, base_indent: int) -> tuple[object, int]:
        i = start
        if i >= len(tokens):
            return {}, i
        block_indent = tokens[i][0]

        if tokens[i][1].startswith("- "):
            items: list[str] = []
            while i < len(tokens) and tokens[i][0] == block_indent:
                line = tokens[i][1]
                if line.startswith("- "):
                    items.append(parse_value(line[2:]))
                    i += 1
                else:
                    break
            return items, i

        mapping: dict = {}
        while i < len(tokens) and tokens[i][0] >= block_indent:
            indent, line = tokens[i]
            if indent != block_indent:
                break
            if ":" in line:
                key, _, rest = line.partition(":")
                key = key.strip()
                rest = rest.strip()
                if rest:
                    mapping[key] = parse_value(rest)
                    i += 1
                else:
                    i += 1
                    if i < len(tokens) and tokens[i][0] > block_indent:
                        value, i = parse_block(i, block_indent)
                        mapping[key] = value
                    else:
                        mapping[key] = {}
            else:
                i += 1
        return mapping, i

    if not tokens:
        return {}
    result, _ = parse_block(0, -1)
    return result if isinstance(result, dict) else {}


def load_manifest(repo_root: Path) -> dict:
    """
    Load .claude/scope.yaml relative to repo_root.
    Returns the parsed dict.  Raises FileNotFoundError if missing, ValueError
    if it does not parse to a dict.
    """
    scope_path = repo_root / ".claude" / "scope.yaml"
    text = scope_path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore[import-untyped]
        result = yaml.safe_load(text) or {}
    except ImportError:
        result = _parse_yaml_minimal(text)
    if not isinstance(result, dict):
        raise ValueError(f"{scope_path} did not parse to a mapping")
    return result


def _get_allow_list(manifest: dict, agent: str) -> list[str]:
    """Return the allow list for *agent* (or main_session if agent == 'main_session')."""
    if agent == "main_session":
        cfg = manifest.get("main_session", {}) or {}
        allow = cfg.get("allow", []) if isinstance(cfg, dict) else []
    else:
        agents = manifest.get("agents", {}) or {}
        if not isinstance(agents, dict) or agent not in agents:
            raise KeyError(f"Agent '{agent}' not found in scope.yaml")
        agent_data = agents[agent]
        allow = agent_data.get("allow", []) if isinstance(agent_data, dict) else []
    return allow if isinstance(allow, list) else []


def _normalize(path: str) -> str:
    """Normalise path separators to forward-slash POSIX form."""
    return PurePosixPath(path.replace("\\", "/")).as_posix()


def matching_glob(manifest: dict, agent: str, rel_path: str) -> str | None:
    """
    Return the first glob pattern from *agent*'s allow list that matches
    *rel_path*, or None if no pattern matches.

    Raises KeyError if *agent* is unknown (not in manifest.agents and not
    'main_session').
    """
    allow_list = _get_allow_list(manifest, agent)
    rel_posix = _normalize(rel_path)
    for pattern in allow_list:
        pat_posix = pattern.replace("\\", "/")
        if fnmatch.fnmatch(rel_posix, pat_posix):
            return pattern
    return None


def agent_allows(manifest: dict, agent: str, rel_path: str) -> bool:
    """
    Return True if *rel_path* matches any glob in *agent*'s allow list.

    Raises KeyError if *agent* is unknown.
    """
    return matching_glob(manifest, agent, rel_path) is not None
