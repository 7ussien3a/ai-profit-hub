#!/usr/bin/env python3
"""Dependency-free, Vault-scoped MCP server for AI Profit Hub Obsidian notes."""

from __future__ import annotations

import contextlib
import io
import json
import os
import re
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
VAULT = (ROOT / "content").resolve()
SCRIPTS = ROOT / "scripts"
MAX_NOTE_BYTES = 2 * 1024 * 1024
EXCLUDED_PARTS = {".obsidian", ".trash", ".git", "node_modules"}
PROTECTED_NAMES = {"credentials.json", "service-account.json"}
ARABIC_SCRIPT_RE = re.compile(r"[\u0600-\u06ff]")
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")

sys.path.insert(0, str(SCRIPTS))
import content_pipeline as pipeline  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


class VaultError(RuntimeError):
    """Raised when a request violates the fixed Vault boundary."""


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _normalise_note_path(note_path: str) -> PurePosixPath:
    value = note_path.strip().replace("\\", "/")
    candidate = PurePosixPath(value)
    if (
        not value
        or candidate.is_absolute()
        or re.match(r"^[A-Za-z]:/", value)
        or ".." in candidate.parts
    ):
        raise VaultError("Note paths must be relative to the AI Profit Hub Vault.")
    if candidate.suffix.casefold() != ".md":
        raise VaultError("Only Markdown note paths are allowed.")
    if any(part.casefold() in EXCLUDED_PARTS for part in candidate.parts):
        raise VaultError("The requested path is excluded from the Vault integration.")
    if any(part.casefold() in PROTECTED_NAMES for part in candidate.parts):
        raise VaultError("Protected credential paths are not accessible.")
    return candidate


def resolve_note_path(note_path: str, *, must_exist: bool = False) -> Path:
    relative = _normalise_note_path(note_path)
    candidate = (VAULT / Path(*relative.parts)).resolve()
    try:
        candidate.relative_to(VAULT)
    except ValueError as exc:
        raise VaultError("The requested path escapes the AI Profit Hub Vault.") from exc
    if must_exist and not candidate.is_file():
        raise VaultError("The requested note does not exist.")
    if candidate.exists() and candidate.is_symlink():
        raise VaultError("Symbolic-link notes are not supported.")
    return candidate


def iter_notes(folder: str = "") -> list[Path]:
    base = VAULT
    if folder.strip():
        relative = PurePosixPath(folder.strip().replace("\\", "/"))
        if relative.is_absolute() or ".." in relative.parts:
            raise VaultError("Folder paths must stay inside the AI Profit Hub Vault.")
        if any(part.casefold() in EXCLUDED_PARTS for part in relative.parts):
            raise VaultError("The requested folder is excluded.")
        base = (VAULT / Path(*relative.parts)).resolve()
        try:
            base.relative_to(VAULT)
        except ValueError as exc:
            raise VaultError("The requested folder escapes the Vault.") from exc
    if not base.exists():
        return []
    notes = []
    for path in base.rglob("*.md"):
        relative = path.relative_to(VAULT)
        if EXCLUDED_PARTS.intersection(part.casefold() for part in relative.parts):
            continue
        if ".backup-" in path.name:
            continue
        resolved = path.resolve()
        try:
            resolved.relative_to(VAULT)
        except ValueError:
            continue
        notes.append(path)
    return sorted(notes, key=lambda path: path.relative_to(VAULT).as_posix().casefold())


def _read_text(path: Path) -> str:
    if path.stat().st_size > MAX_NOTE_BYTES:
        raise VaultError("The note exceeds the integration size limit.")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise VaultError("The note is not valid UTF-8.") from exc


def _frontmatter(text: str, path: Path) -> dict[str, Any]:
    if not text.startswith("---"):
        return {}
    try:
        metadata, _ = pipeline.parse_frontmatter(text, path)
        return metadata
    except ValueError:
        return {}


def list_notes(folder: str = "", limit: int = 200) -> dict[str, Any]:
    safe_limit = min(max(int(limit), 1), 500)
    notes = []
    for path in iter_notes(folder)[:safe_limit]:
        stat = path.stat()
        notes.append(
            {
                "path": path.relative_to(VAULT).as_posix(),
                "sizeBytes": stat.st_size,
                "modifiedAt": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
            }
        )
    return {"vault": str(VAULT), "notes": notes, "count": len(notes)}


def read_note(note_path: str) -> dict[str, Any]:
    path = resolve_note_path(note_path, must_exist=True)
    text = _read_text(path)
    return {
        "path": path.relative_to(VAULT).as_posix(),
        "frontmatter": _frontmatter(text, path),
        "content": text,
    }


def _validate_write_content(content: str) -> bytes:
    encoded = content.encode("utf-8")
    if len(encoded) > MAX_NOTE_BYTES:
        raise VaultError("The note exceeds the integration size limit.")
    if ARABIC_SCRIPT_RE.search(content):
        raise VaultError("AI Profit Hub tracked notes must remain English-only.")
    return encoded


def _atomic_write(path: Path, content: str) -> None:
    encoded = _validate_write_content(content)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        Path(temp_name).replace(path)
    finally:
        Path(temp_name).unlink(missing_ok=True)


def create_note(note_path: str, content: str) -> dict[str, Any]:
    path = resolve_note_path(note_path)
    if path.exists():
        raise VaultError("The note already exists; create never overwrites notes.")
    _atomic_write(path, content)
    return {"created": path.relative_to(VAULT).as_posix(), "updatedAt": _now()}


def update_note(note_path: str, content: str) -> dict[str, Any]:
    path = resolve_note_path(note_path, must_exist=True)
    _atomic_write(path, content)
    return {"updated": path.relative_to(VAULT).as_posix(), "updatedAt": _now()}


def search_notes(query: str, folder: str = "", limit: int = 50) -> dict[str, Any]:
    needle = query.strip().casefold()
    if not needle:
        raise VaultError("Search query cannot be empty.")
    safe_limit = min(max(int(limit), 1), 200)
    matches = []
    for path in iter_notes(folder):
        text = _read_text(path)
        haystack = f"{path.name}\n{text}".casefold()
        if needle not in haystack:
            continue
        index = haystack.find(needle)
        snippet = re.sub(r"\s+", " ", text[max(0, index - 80) : index + len(needle) + 120]).strip()
        matches.append(
            {
                "path": path.relative_to(VAULT).as_posix(),
                "snippet": snippet[:240],
            }
        )
        if len(matches) >= safe_limit:
            break
    return {"query": query, "matches": matches, "count": len(matches)}


def _note_lookup() -> dict[str, list[str]]:
    lookup: dict[str, list[str]] = {}
    for path in iter_notes():
        relative = path.relative_to(VAULT).as_posix()
        text = _read_text(path)
        metadata = _frontmatter(text, path)
        keys = {
            path.stem,
            relative.removesuffix(".md"),
            str(metadata.get("title") or "").strip(),
        }
        for key in keys:
            normalised = re.sub(r"\s+", " ", key.strip().casefold())
            if normalised:
                lookup.setdefault(normalised, []).append(relative)
    for title, public_path in pipeline.collect_legacy_titles().items():
        for key in {title, Path(public_path).stem}:
            normalised = re.sub(r"\s+", " ", key.strip().casefold())
            if normalised and normalised not in lookup:
                lookup[normalised] = [f"public:{public_path}"]
    return lookup


def resolve_links(note_path: str) -> dict[str, Any]:
    path = resolve_note_path(note_path, must_exist=True)
    text = _read_text(path)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    lookup = _note_lookup()
    links = []
    for raw_target in WIKILINK_RE.findall(text):
        target = raw_target.split("#", 1)[0].strip()
        key = re.sub(r"\s+", " ", target.casefold())
        matches = sorted(set(lookup.get(key, [])))
        status = "resolved" if len(matches) == 1 else "ambiguous" if matches else "missing"
        links.append({"target": raw_target, "status": status, "matches": matches})
    return {
        "path": path.relative_to(VAULT).as_posix(),
        "links": links,
        "valid": all(link["status"] == "resolved" for link in links),
    }


def _validate_editorial_metadata(path: Path, text: str) -> list[str]:
    relative = path.relative_to(VAULT)
    if not pipeline.EDITORIAL_ONLY_FOLDERS.intersection(relative.parts):
        return []
    metadata = _frontmatter(text, path)
    if not metadata:
        return []
    required = {"title", "noteType", "status", "updatedAt", "language"}
    issues = [f"missing {key}" for key in sorted(required) if not metadata.get(key)]
    allowed_types = {"source", "research", "go-cycle-report", "editorial-update"}
    if metadata.get("noteType") not in allowed_types:
        issues.append("invalid noteType")
    if metadata.get("language") != "en":
        issues.append("language must be en")
    return issues


def validate_vault() -> dict[str, Any]:
    issues = []
    warnings = []
    required_paths = [
        VAULT / ".obsidian" / "app.json",
        VAULT / ".obsidian" / "templates.json",
        VAULT / "content.schema.json",
        VAULT / "editorial-note.schema.json",
        VAULT / "Dashboard.md",
        VAULT / "templates",
        VAULT / "assets",
    ]
    for path in required_paths:
        if not path.exists():
            issues.append(f"missing required Vault path: {path.relative_to(VAULT)}")
    for protected in PROTECTED_NAMES:
        if any(path.name.casefold() == protected for path in VAULT.rglob("*")):
            issues.append(f"protected file is present inside the Vault: {protected}")
    for path in iter_notes():
        relative = path.relative_to(VAULT).as_posix()
        try:
            text = _read_text(path)
        except VaultError as exc:
            issues.append(f"{relative}: {exc}")
            continue
        if ARABIC_SCRIPT_RE.search(text):
            issues.append(f"{relative}: Arabic script is not allowed")
        for metadata_issue in _validate_editorial_metadata(path, text):
            issues.append(f"{relative}: {metadata_issue}")
        link_result = resolve_links(relative)
        for link in link_result["links"]:
            if link["status"] != "resolved":
                issues.append(f"{relative}: {link['status']} Wiki Link: {link['target']}")
    pipeline_stdout = io.StringIO()
    pipeline_stderr = io.StringIO()
    with contextlib.redirect_stdout(pipeline_stdout), contextlib.redirect_stderr(pipeline_stderr):
        pipeline_code = pipeline.validate(pipeline.load_content())
    if pipeline_code != 0:
        issues.append("content pipeline validation failed")
    pipeline_output = (pipeline_stdout.getvalue() + pipeline_stderr.getvalue()).strip()
    if "WARNING:" in pipeline_output:
        warnings.append("content pipeline reported draft warnings")
    return {
        "status": "PASS" if not issues else "FAIL",
        "vaultPath": str(VAULT),
        "noteCount": len(iter_notes()),
        "issues": issues,
        "warnings": warnings,
        "contentPipelineExitCode": pipeline_code,
        "contentPipelineOutput": pipeline_output,
    }


def health_check() -> dict[str, Any]:
    validation = validate_vault()
    return {
        "status": validation["status"],
        "server": "ai-profit-hub-obsidian-local",
        "vaultPath": str(VAULT),
        "vaultAccessible": VAULT.is_dir(),
        "vaultWritable": os.access(VAULT, os.W_OK),
        "noteCount": validation["noteCount"],
        "issues": validation["issues"],
    }


TOOLS: list[dict[str, Any]] = [
    {
        "name": "obsidian_health_check",
        "description": "Verify the isolated AI Profit Hub Vault and publishing-pipeline connection.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "obsidian_vault_path",
        "description": "Return the fixed AI Profit Hub Vault path and isolation boundary.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "obsidian_list_notes",
        "description": "List Markdown notes inside the AI Profit Hub Vault.",
        "inputSchema": {
            "type": "object",
            "properties": {"folder": {"type": "string"}, "limit": {"type": "integer"}},
        },
    },
    {
        "name": "obsidian_read_note",
        "description": "Read one Markdown note inside the AI Profit Hub Vault.",
        "inputSchema": {
            "type": "object",
            "required": ["path"],
            "properties": {"path": {"type": "string"}},
        },
    },
    {
        "name": "obsidian_create_note",
        "description": "Explicitly create an English Markdown note without overwriting existing work.",
        "inputSchema": {
            "type": "object",
            "required": ["path", "content"],
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
        },
    },
    {
        "name": "obsidian_update_note",
        "description": "Explicitly update an existing English Markdown note inside the Vault.",
        "inputSchema": {
            "type": "object",
            "required": ["path", "content"],
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
        },
    },
    {
        "name": "obsidian_search_notes",
        "description": "Search AI Profit Hub note paths and text.",
        "inputSchema": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {"type": "string"},
                "folder": {"type": "string"},
                "limit": {"type": "integer"},
            },
        },
    },
    {
        "name": "obsidian_resolve_links",
        "description": "Resolve Wiki Links from one AI Profit Hub note.",
        "inputSchema": {
            "type": "object",
            "required": ["path"],
            "properties": {"path": {"type": "string"}},
        },
    },
    {
        "name": "obsidian_validate_vault",
        "description": "Validate Vault configuration, notes, Wiki Links, language, and pipeline readiness.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def _tool_result(value: Any, *, is_error: bool = False) -> dict[str, Any]:
    return {
        "content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False, indent=2)}],
        "isError": is_error,
    }


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    handlers: dict[str, Callable[[], Any]] = {
        "obsidian_health_check": health_check,
        "obsidian_vault_path": lambda: {
            "server": "ai-profit-hub-obsidian-local",
            "vaultPath": str(VAULT),
            "fixedBoundary": True,
        },
        "obsidian_list_notes": lambda: list_notes(
            str(arguments.get("folder", "")), int(arguments.get("limit", 200))
        ),
        "obsidian_read_note": lambda: read_note(str(arguments["path"])),
        "obsidian_create_note": lambda: create_note(
            str(arguments["path"]), str(arguments["content"])
        ),
        "obsidian_update_note": lambda: update_note(
            str(arguments["path"]), str(arguments["content"])
        ),
        "obsidian_search_notes": lambda: search_notes(
            str(arguments["query"]),
            str(arguments.get("folder", "")),
            int(arguments.get("limit", 50)),
        ),
        "obsidian_resolve_links": lambda: resolve_links(str(arguments["path"])),
        "obsidian_validate_vault": validate_vault,
    }
    if name not in handlers:
        raise VaultError(f"Unknown MCP tool: {name}")
    return _tool_result(handlers[name]())


def _response(
    request_id: Any,
    result: dict[str, Any] | None = None,
    error: dict[str, Any] | None = None,
) -> dict[str, Any]:
    message: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id}
    message["error" if error else "result"] = error or result or {}
    return message


def handle(request: dict[str, Any]) -> dict[str, Any] | None:
    request_id = request.get("id")
    method = request.get("method")
    if request_id is None:
        return None
    if method == "initialize":
        return _response(
            request_id,
            {
                "protocolVersion": request.get("params", {}).get(
                    "protocolVersion", "2024-11-05"
                ),
                "serverInfo": {
                    "name": "ai-profit-hub-obsidian-local",
                    "version": "1.0.0",
                },
                "capabilities": {"tools": {}},
            },
        )
    if method == "tools/list":
        return _response(request_id, {"tools": TOOLS})
    if method == "tools/call":
        params = request.get("params", {})
        try:
            return _response(
                request_id,
                call_tool(
                    str(params.get("name", "")),
                    dict(params.get("arguments", {})),
                ),
            )
        except (KeyError, TypeError, ValueError, VaultError, OSError) as exc:
            return _response(request_id, _tool_result({"error": str(exc)}, is_error=True))
    if method == "ping":
        return _response(request_id, {})
    return _response(
        request_id,
        error={"code": -32601, "message": f"Method not found: {method}"},
    )


def self_test() -> int:
    result = health_check()
    result["pathEscapeBlocked"] = False
    try:
        resolve_note_path("../../credentials.json")
    except VaultError:
        result["pathEscapeBlocked"] = True
    result["protectedExtensionBlocked"] = False
    try:
        resolve_note_path("credentials.json")
    except VaultError:
        result["protectedExtensionBlocked"] = True
    result["toolCount"] = len(TOOLS)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" and result["pathEscapeBlocked"] else 1


def main() -> int:
    if "--self-test" in sys.argv[1:]:
        return self_test()
    for raw_line in sys.stdin:
        try:
            response = handle(json.loads(raw_line))
            if response is not None:
                print(json.dumps(response, ensure_ascii=False), flush=True)
        except json.JSONDecodeError as exc:
            print(f"Invalid MCP JSON: {exc}", file=sys.stderr, flush=True)
        except Exception as exc:
            print(
                f"Unexpected MCP server error: {type(exc).__name__}",
                file=sys.stderr,
                flush=True,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
