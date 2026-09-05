#!/usr/bin/env python3
"""
FULL DIAGNOSTIC — AniList → MyAnimeList manual sync

Run from the root of your Anilist-triple-sync repository:

    py diagnose_mal_sync.py

Optional:
    py diagnose_mal_sync.py --engine mal_sync_engine.py
    py diagnose_mal_sync.py --workflow .github/workflows/mal_sync_manual.yml

This is primarily a STATIC / SAFETY diagnostic. It does not print secrets.
It checks the engine, workflow, state persistence design, delta logic,
MAL/AniList mappings, common API mistakes, and likely data-loss conditions.

Exit codes:
    0 = no ERROR findings
    1 = one or more ERROR findings
    2 = diagnostic itself could not run
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Iterable


RESET = "\033[0m"
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
BOLD = "\033[1m"


def c(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


errors: list[str] = []
warnings: list[str] = []
infos: list[str] = []


def error(msg: str) -> None:
    errors.append(msg)
    print(c(f"[ERROR] {msg}", RED))


def warning(msg: str) -> None:
    warnings.append(msg)
    print(c(f"[WARN ] {msg}", YELLOW))


def info(msg: str) -> None:
    infos.append(msg)
    print(c(f"[INFO ] {msg}", CYAN))


def ok(msg: str) -> None:
    print(c(f"[ OK  ] {msg}", GREEN))


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        raise RuntimeError(f"Could not read {path}: {exc}") from exc


def line_number(text: str, needle: str) -> int | None:
    for i, line in enumerate(text.splitlines(), 1):
        if needle in line:
            return i
    return None


def find_function(tree: ast.AST, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    return None


def function_names(tree: ast.AST) -> set[str]:
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def collect_called_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                names.add(node.func.attr)
    return names


def parse_yaml_like(text: str) -> dict[str, object]:
    """
    Lightweight YAML inspection without requiring PyYAML.
    We intentionally inspect text because the workflow is simple and GitHub
    Actions syntax uses several constructs that do not need full YAML parsing.
    """
    return {
        "manual": bool(re.search(r"(?m)^\s*workflow_dispatch\s*:\s*$", text)),
        "contents_write": bool(
            re.search(r"(?m)^\s*contents:\s*write\s*$", text)
        ),
        "checkout_fetch_depth_0": bool(
            re.search(r"(?m)^\s*fetch-depth:\s*0\s*$", text)
        ),
        "git_fetch": "git fetch" in text,
        "git_rebase": "git rebase" in text,
        "git_push": "git push" in text,
        "state_file": "mal_delta_state.json" in text,
        "state_commit": bool(
            re.search(r"git\s+commit\b", text)
            and "mal_delta_state.json" in text
        ),
        "secrets": {
            name: name in text
            for name in (
                "ANILIST_TARGET_TOKEN",
                "MAL_CLIENT_ID",
                "MAL_CLIENT_SECRET",
                "MAL_REFRESH_TOKEN",
            )
        },
    }


def has_full_mal_library_scan(text: str) -> bool:
    # Known full-library endpoint / loop indicators.
    patterns = [
        r"/v2/users/@me/animelist",
        r"@me/animelist",
    ]
    return any(re.search(p, text) for p in patterns)


def has_targeted_mal_lookup(text: str) -> bool:
    return (
        "my_list_status" in text
        and "/v2/anime/{anime_id}" in text
    )


def has_state_persistence(text: str) -> bool:
    return "mal_delta_state.json" in text and "save_state" in text


def inspect_engine(path: Path) -> None:
    print()
    print(c("=" * 72, BOLD))
    print(c(f"ENGINE: {path}", BOLD))
    print(c("=" * 72, BOLD))

    if not path.exists():
        error(f"Engine file does not exist: {path}")
        return

    text = read_text(path)

    try:
        tree = ast.parse(text, filename=str(path))
        ok("Python syntax is valid.")
    except SyntaxError as exc:
        error(
            f"Python syntax error at line {exc.lineno}, column {exc.offset}: "
            f"{exc.msg}"
        )
        return

    funcs = function_names(tree)
    called = collect_called_names(tree)

    # Imports
    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module.split(".")[0])

    for required in ("os", "json", "time", "requests"):
        if required in imported_modules:
            ok(f"Required import present: {required}")
        else:
            error(f"Required import missing: {required}")

    # Core functions
    required_functions = [
        "load_state",
        "save_state",
        "require_config",
        "request_with_retry",
        "refresh_mal_token",
        "fetch_anilist_delta",
        "fetch_mal_entry",
        "sync_entry",
        "main",
    ]

    for fn in required_functions:
        if fn in funcs:
            ok(f"Core function present: {fn}()")
        else:
            error(f"Core function missing: {fn}()")

    # Calls to locally defined functions
    missing_local_calls = sorted(
        name
        for name in called
        if name.startswith(("fetch_", "save_", "load_", "sync_", "refresh_", "require_"))
        and name not in funcs
    )
    if missing_local_calls:
        for name in missing_local_calls:
            error(f"Engine calls undefined local function: {name}()")

    # Required variables / secrets
    for secret in (
        "ANILIST_TARGET_TOKEN",
        "MAL_CLIENT_ID",
        "MAL_CLIENT_SECRET",
        "MAL_REFRESH_TOKEN",
    ):
        if secret in text:
            ok(f"Secret variable referenced: {secret}")
        else:
            error(f"Expected secret variable not referenced: {secret}")

    # Delta behavior
    if "updatedAt" in text:
        ok("AniList updatedAt is part of the query.")
    else:
        error("AniList query does not request updatedAt.")

    if "UPDATED_TIME_DESC" in text:
        ok("AniList entries are requested newest-first.")
    else:
        warning("AniList query is not explicitly sorted by UPDATED_TIME_DESC.")

    if "last_anilist_update" in text or "media_updates" in text:
        ok("Persistent delta cursor/state is implemented.")
    else:
        error("No persistent AniList delta state detected.")

    if re.search(r"if\s+last_sync\b", text):
        ok("Code contains a delta boundary check.")
    else:
        warning("Could not detect a last_sync delta boundary.")

    # MAL scan
    if has_full_mal_library_scan(text):
        error(
            "Engine references /users/@me/animelist. "
            "That is a full MAL library endpoint and violates the requested "
            "short-update design if it is used for every run."
        )
    else:
        ok("No full MAL user-library endpoint detected.")

    if has_targeted_mal_lookup(text):
        ok("Targeted MAL anime lookup is present.")
    else:
        error(
            "Targeted MAL lookup was not detected "
            "(expected /v2/anime/{anime_id} with my_list_status)."
        )

    # State write safety
    if has_state_persistence(text):
        ok("State file persistence code is present.")
    else:
        error("State file persistence code is missing.")

    # Refresh token
    if "refresh_token" in text and "new_refresh_token" in text:
        ok("Refresh-token rotation is detected by the engine.")
        if "Update MAL_REFRESH_TOKEN" in text:
            warning(
                "Engine can detect rotation but still relies on a manual "
                "GitHub Secret update unless workflow updates the secret."
            )
    else:
        error("Refresh-token rotation handling is missing.")

    # Score
    if "score <= 0" in text and "return None" in text:
        warning(
            "Score conversion treats 0 as None. "
            "If AniList score 0 means 'clear rating', MAL should receive "
            "score=0 to remove the old rating."
        )
    if re.search(r'update_data\["score"\]', text):
        ok("MAL score update field is supported by the engine.")

    # Dates
    if "start_date" in text and "finish_date" in text:
        ok("Start/finish date fields are handled.")
        if 'desired_start and desired_start != current_start' in text:
            ok("Start-date changes are compared.")
        if 'desired_finish' in text and 'current_finish' in text:
            ok("Finish-date changes are compared.")
    else:
        warning("Start/finish date synchronization is incomplete or absent.")

    # Deletion / removal behavior
    deletion_markers = (
        "deleted",
        "removed",
        "not_in_anilist",
        "not found in anilist",
        "missing_from_anilist",
    )
    if any(marker.lower() in text.lower() for marker in deletion_markers):
        info("Engine contains some deletion/removal terminology.")
    else:
        warning(
            "No AniList deletion/removal detection was found. "
            "Removing an anime from AniList may not remove it from MAL."
        )

    # Rewatch
    if "REPEATING" in text and "is_rewatching" not in text:
        warning(
            "AniList REPEATING maps to MAL watching, but MAL rewatch state "
            "does not appear to be synchronized."
        )

    # Timestamp / fingerprint
    if "fingerprint" in text:
        ok("Per-entry fingerprint concept detected.")
    else:
        warning(
            "No entry fingerprint detected. "
            "A timestamp-only strategy can have edge cases around equal timestamps."
        )

    # Fail-safe state movement
    if "successful_media_ids" in text:
        ok("State advancement appears to distinguish successful entries.")
    else:
        warning(
            "Could not find per-entry success tracking. "
            "A failed MAL update may advance the global cursor and be skipped."
        )

    # Requests / methods
    if "grant_type" in text and "refresh_token" in text:
        ok("MAL refresh-token grant is present.")
    else:
        error("MAL refresh-token grant is missing.")

    if re.search(r'requests\.request\(\s*method', text):
        ok("HTTP calls use a common retry wrapper.")
    else:
        warning("Could not verify common HTTP retry wrapper use.")

    # Dangerous output checks
    if "print(MAL_CLIENT_SECRET" in text or "print(client_secret" in text:
        error("Client Secret may be printed by the engine.")
    else:
        ok("No obvious direct Client Secret print detected.")

    # State file integrity
    if 'os.replace(tmp, STATE_FILE)' in text:
        ok("State writes use atomic os.replace().")
    else:
        warning("State file writes do not show atomic replacement.")

    # Hardcoded account
    if 'SOURCE_USERNAME = "Orewatokyo"' in text:
        info("Source username is hardcoded as Orewatokyo.")
    else:
        warning("Source username hardcoding could not be verified.")

    # Pagination
    if "hasNextPage" in text and "page += 1" in text:
        ok("AniList pagination is implemented.")
    else:
        warning("Could not verify AniList pagination.")

    # Empty library behavior
    if "changed_entries" in text:
        ok("Changed-entry collection is present.")
    else:
        error("No changed-entry collection detected.")


def inspect_workflow(path: Path) -> None:
    print()
    print(c("=" * 72, BOLD))
    print(c(f"WORKFLOW: {path}", BOLD))
    print(c("=" * 72, BOLD))

    if not path.exists():
        error(f"Workflow file does not exist: {path}")
        return

    text = read_text(path)
    y = parse_yaml_like(text)

    if y["manual"]:
        ok("Workflow is manually triggerable via workflow_dispatch.")
    else:
        error("workflow_dispatch trigger not found.")

    # Check for unwanted automatic triggers.
    automatic_triggers = []
    for trigger in ("push", "pull_request", "schedule", "workflow_run"):
        if re.search(rf"(?m)^\s*{re.escape(trigger)}\s*:", text):
            automatic_triggers.append(trigger)

    if automatic_triggers:
        warning(
            "Additional workflow triggers detected: "
            + ", ".join(automatic_triggers)
        )
    else:
        ok("No push/pull_request/schedule/workflow_run trigger detected.")

    if y["contents_write"]:
        ok("Workflow has contents: write permission for state persistence.")
    else:
        error("Workflow lacks contents: write permission.")

    if y["checkout_fetch_depth_0"]:
        ok("Checkout uses fetch-depth: 0.")
    else:
        warning(
            "fetch-depth: 0 was not detected. "
            "Rebase/push logic may lack sufficient history."
        )

    if y["git_fetch"]:
        ok("Workflow fetches remote main.")
    else:
        error("Workflow does not fetch origin/main before persistence.")

    if y["git_rebase"]:
        ok("Workflow has rebase logic.")
    else:
        warning("No git rebase detected in state persistence step.")

    if y["git_push"]:
        ok("Workflow pushes persisted state.")
    else:
        error("Workflow does not push persisted state.")

    if y["state_file"]:
        ok("Workflow knows about mal_delta_state.json.")
    else:
        error("Workflow does not reference mal_delta_state.json.")

    if y["state_commit"]:
        ok("Workflow commits state changes.")
    else:
        error("Workflow does not clearly commit delta state.")

    for secret, present in y["secrets"].items():
        if present:
            ok(f"Workflow references secret: {secret}")
        else:
            error(f"Workflow missing required secret: {secret}")

    # Danger: secrets must not be echoed.
    if re.search(r"echo\s+.*MAL_CLIENT_SECRET", text):
        error("Workflow may echo MAL_CLIENT_SECRET.")
    else:
        ok("No obvious secret echo detected.")

    # Runner should use correct script
    if "python mal_sync_engine.py" in text:
        ok("Workflow runs mal_sync_engine.py.")
    else:
        warning(
            "Workflow does not appear to run mal_sync_engine.py; "
            "check that the intended engine is actually being executed."
        )

    # Concurrency
    if "concurrency:" in text:
        ok("Concurrency control is present.")
    else:
        warning(
            "No GitHub Actions concurrency group detected. "
            "Two manual runs could race to update state."
        )

    # Push to main
    if "HEAD:main" in text:
        ok("State push targets main.")
    elif re.search(r"git\s+push\b", text):
        warning("Push command detected, but HEAD:main was not found.")

    # Error handling
    if "for attempt in 1 2 3" in text:
        ok("Persistence push has retry attempts.")
    else:
        warning("No explicit multi-attempt push retry loop detected.")


def inspect_state_file(path: Path) -> None:
    print()
    print(c("=" * 72, BOLD))
    print(c(f"STATE FILE CHECK", BOLD))
    print(c("=" * 72, BOLD))

    if not path.exists():
        info(
            f"{path} does not exist in the local checkout. "
            "This is normal before the engine has created it."
        )
        return

    try:
        data = json.loads(read_text(path))
    except Exception as exc:
        error(f"State file is invalid JSON: {exc}")
        return

    if not isinstance(data, dict):
        error("State file root is not a JSON object.")
        return

    ok("State file is valid JSON.")

    for key in ("last_anilist_update", "media_updates"):
        if key in data:
            ok(f"State key present: {key}")
        else:
            warning(f"State key missing: {key}")

    if "media_updates" in data:
        media_updates = data["media_updates"]
        if isinstance(media_updates, dict):
            info(f"Stored per-media entries: {len(media_updates)}")
        else:
            error("media_updates exists but is not an object.")

    if "last_anilist_update" in data:
        try:
            cursor = int(data["last_anilist_update"])
            if cursor > 0:
                ok(f"AniList cursor is numeric: {cursor}")
            else:
                warning("AniList cursor is zero/non-positive.")
        except Exception:
            error("AniList cursor is not an integer.")


def inspect_repo_shape(root: Path, engine: Path, workflow: Path) -> None:
    print()
    print(c("=" * 72, BOLD))
    print(c("REPOSITORY SHAPE", BOLD))
    print(c("=" * 72, BOLD))

    if engine.parent == root:
        ok("Engine is at repository root.")
    else:
        info(f"Engine path: {engine}")

    if ".github" in workflow.parts and "workflows" in workflow.parts:
        ok("Workflow is under .github/workflows.")
    else:
        warning("Workflow path is not under .github/workflows.")

    # Detect duplicate MAL engines that may cause confusion.
    candidates = sorted(root.glob("*mal*sync*.py"))
    if len(candidates) > 1:
        warning(
            "Multiple MAL sync Python files detected: "
            + ", ".join(p.name for p in candidates)
        )
    else:
        ok("No obvious duplicate MAL sync engine filenames detected.")


def run_basic_behavioral_checks(engine: Path) -> None:
    """
    Lightweight source-level checks for exact patterns likely to matter.
    No API calls are made.
    """
    print()
    print(c("=" * 72, BOLD))
    print(c("BEHAVIORAL SAFETY CHECKS", BOLD))
    print(c("=" * 72, BOLD))

    text = read_text(engine)

    # Verify the MAL update method.
    if re.search(r'MAL_UPDATE_URL\s*=.*my_list_status', text):
        ok("MAL update endpoint pattern is present.")
    else:
        error("MAL update endpoint pattern not found.")

    if re.search(r'"num_watched_episodes"', text):
        ok("Watched-episode update field is present.")
    else:
        error("num_watched_episodes update field is missing.")

    # Status map
    for status in (
        "CURRENT",
        "REPEATING",
        "PLANNING",
        "COMPLETED",
        "PAUSED",
        "DROPPED",
    ):
        if status in text:
            ok(f"AniList status mapped/considered: {status}")
        else:
            warning(f"AniList status not found in engine: {status}")

    # Don't accidentally modify AniList.
    if "SaveMediaListEntry" in text:
        error(
            "Engine contains SaveMediaListEntry. "
            "That means it can write back to AniList; verify this one-way "
            "MAL engine is not modifying the source account."
        )
    else:
        ok("No SaveMediaListEntry write-back detected.")

    # Don't run on manga.
    if re.search(r"type:\s*MANGA", text) or 'type": "MANGA"' in text:
        warning("MANGA logic detected in the MAL anime sync engine.")
    else:
        ok("No obvious Manga GraphQL target detected.")

    # Full scan loops against MAL list
    if "@me/animelist" in text:
        error("Full MAL library scan marker detected.")
    else:
        ok("No @me/animelist full-library scan marker.")

    # State should not be reset every run.
    if "save_state({\"last_anilist_update\"" in text:
        warning(
            "Engine has a direct baseline write pattern. "
            "Verify it executes only when state is missing, not every run."
        )

    # Retry after 401
    if "status_code == 401" in text and "refresh_mal_token()" in text:
        ok("401 → token refresh/retry path detected.")
    else:
        warning("Could not verify 401 token refresh/retry path.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Full diagnostic for AniList → MAL sync."
    )
    parser.add_argument(
        "--engine",
        default="mal_sync_engine.py",
        help="Path to engine (default: mal_sync_engine.py)",
    )
    parser.add_argument(
        "--workflow",
        default=".github/workflows/mal_sync_manual.yml",
        help="Path to workflow",
    )
    parser.add_argument(
        "--state",
        default="mal_delta_state.json",
        help="Path to delta state",
    )
    args = parser.parse_args()

    root = Path.cwd()
    engine = Path(args.engine)
    workflow = Path(args.workflow)
    state = Path(args.state)

    print(c("=" * 72, BOLD))
    print(c("FULL MAL SYNC DIAGNOSTIC", BOLD))
    print(c("=" * 72, BOLD))
    print(f"Repository root : {root}")
    print(f"Engine          : {engine}")
    print(f"Workflow        : {workflow}")
    print(f"State           : {state}")
    print()

    if not engine.is_absolute():
        engine = root / engine
    if not workflow.is_absolute():
        workflow = root / workflow
    if not state.is_absolute():
        state = root / state

    inspect_repo_shape(root, engine, workflow)
    inspect_engine(engine)
    inspect_workflow(workflow)
    inspect_state_file(state)

    if engine.exists():
        run_basic_behavioral_checks(engine)

    print()
    print(c("=" * 72, BOLD))
    print(c("DIAGNOSTIC SUMMARY", BOLD))
    print(c("=" * 72, BOLD))
    print(c(f"ERRORS   : {len(errors)}", RED if errors else GREEN))
    print(c(f"WARNINGS : {len(warnings)}", YELLOW if warnings else GREEN))
    print(c(f"INFO     : {len(infos)}", CYAN))

    print()
    if errors:
        print(c("❌ RESULT: FIX REQUIRED", RED + BOLD))
        return 1

    if warnings:
        print(c("⚠️ RESULT: NO HARD ERROR, BUT REVIEW WARNINGS", YELLOW + BOLD))
        return 0

    print(c("✅ RESULT: NO STATIC PROBLEMS DETECTED", GREEN + BOLD))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nInterrupted.")
        raise SystemExit(2)
    except Exception as exc:
        print(c(f"Diagnostic failed: {exc}", RED))
        raise SystemExit(2)
