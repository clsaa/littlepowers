#!/usr/bin/env python3
"""Arm one bounded Claude Code wake-up for an exact Littlepowers Review Gate."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator

import littlepowers_state as state_module


JOB_VERSION = 1
CLAUDE_TIMEOUT_SECONDS = 3600
JOB_STATUSES = {"armed", "invoking", "completed", "failed", "stale"}
JOB_ERRORS = {
    None,
    "gate_no_gate",
    "gate_waiting",
    "gate_blocked",
    "workflow_changed",
    "state_unavailable",
    "spawn_error",
    "timeout",
    "nonzero_exit",
}
JOB_KEYS = {
    "job_version",
    "root",
    "workflow_id",
    "gate_revision",
    "session_id",
    "not_before",
    "claude_path",
    "status",
    "pid",
    "created_at",
    "updated_at",
    "exit_code",
    "error",
}


class RunnerError(RuntimeError):
    """Raised for an unsafe or invalid one-shot runner operation."""


class JobConflict(RunnerError):
    """Raised when another runner already advanced the exact review job."""


def _job_stat_snapshot(details: os.stat_result) -> tuple[int, ...]:
    """Return one same-interface snapshot for a review-job race check."""

    return (
        details.st_dev,
        details.st_ino,
        details.st_mode,
        details.st_nlink,
        details.st_size,
        details.st_mtime_ns,
        details.st_ctime_ns,
    )


def _job_file_identity(details: os.stat_result) -> tuple[int, int]:
    """Return the cross-interface file identity shared by path and handle stats."""

    return (details.st_dev, details.st_ino)


def _canonical_uuid(value: str, label: str) -> str:
    try:
        parsed = uuid.UUID(value)
    except ValueError as exc:
        raise RunnerError(f"{label} must be a canonical UUID") from exc
    if str(parsed) != value:
        raise RunnerError(f"{label} must be a canonical UUID")
    return value


def _canonical_root(value: str) -> Path:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        raise RunnerError("root must be an absolute path")
    resolved = candidate.resolve()
    if str(resolved) != value:
        raise RunnerError("root must already be canonical")
    if not resolved.is_dir():
        raise RunnerError("root must be an existing directory")
    return resolved


def _parse_timestamp(value: str, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise RunnerError(f"{label} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise RunnerError(f"{label} must include a timezone")
    return parsed


def _job_path(
    root: Path, workflow: str, gate_revision: int
) -> Path:
    return state_module.state_directory(root) / "review-jobs" / (
        f"{workflow}-r{gate_revision}.json"
    )


def _validate_job_store(jobs: Path, details: os.stat_result) -> None:
    attributes = getattr(details, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    if (
        stat.S_ISLNK(details.st_mode)
        or bool(attributes & reparse_flag)
        or not stat.S_ISDIR(details.st_mode)
    ):
        raise RunnerError(f"review job store must be a regular directory: {jobs}")
    try:
        state_module._require_owned_metadata(
            details, jobs, "review job store", single_link=False
        )
    except state_module.StateError as exc:
        raise RunnerError(str(exc)) from exc


@contextmanager
def _open_job_store(
    root: Path, *, create: bool
) -> Iterator[tuple[Path, int | None, bool]]:
    """Pin the state and job directories for one bounded metadata operation."""

    try:
        store, workspace_fd, state_fd = state_module._open_state_store_directory(
            root, create=create
        )
    except state_module.StateError as exc:
        raise RunnerError(str(exc)) from exc
    jobs = state_module.state_directory(root) / "review-jobs"
    jobs_fd: int | None = None
    try:
        if store is None:
            yield jobs, None, False
            return
        if state_fd is None:  # pragma: no cover - exercised in Windows CI
            available = os.path.lexists(jobs)
            initial: os.stat_result | None = None
            if available:
                details = os.lstat(jobs)
                if state_module._is_link_or_reparse(jobs):
                    raise RunnerError(
                        f"review job store must be a regular directory: {jobs}"
                    )
                _validate_job_store(jobs, details)
                initial = details
            elif create:
                try:
                    jobs.mkdir(mode=0o700)
                except OSError as exc:
                    raise RunnerError(
                        f"cannot create review job store {jobs}: {exc}"
                    ) from exc
                initial = os.lstat(jobs)
                _validate_job_store(jobs, initial)
                available = True
            yield jobs, None, available
            if available:
                if not os.path.lexists(jobs):
                    raise RunnerError(
                        f"review job store changed during operation: {jobs}"
                    )
                current = os.lstat(jobs)
                _validate_job_store(jobs, current)
                assert initial is not None
                if (current.st_dev, current.st_ino) != (
                    initial.st_dev,
                    initial.st_ino,
                ):
                    raise RunnerError(
                        f"review job store changed during operation: {jobs}"
                    )
            return

        name = jobs.name
        try:
            details = os.stat(name, dir_fd=state_fd, follow_symlinks=False)
        except FileNotFoundError:
            if not create:
                yield jobs, None, False
                return
            try:
                os.mkdir(name, mode=0o700, dir_fd=state_fd)
                details = os.stat(name, dir_fd=state_fd, follow_symlinks=False)
            except OSError as exc:
                raise RunnerError(
                    f"cannot create review job store {jobs}: {exc}"
                ) from exc
        _validate_job_store(jobs, details)
        flags = (
            os.O_RDONLY
            | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0)
        )
        try:
            jobs_fd = os.open(name, flags, dir_fd=state_fd)
        except OSError as exc:
            raise RunnerError(
                f"cannot safely open review job store {jobs}: {exc}"
            ) from exc
        opened = os.fstat(jobs_fd)
        if (opened.st_dev, opened.st_ino) != (details.st_dev, details.st_ino):
            raise RunnerError(f"review job store changed while opening: {jobs}")
        try:
            state_module._verify_pinned_store_path(root, state_fd)
        except state_module.StateError as exc:
            raise RunnerError(str(exc)) from exc
        yield jobs, jobs_fd, True
        try:
            state_module._verify_pinned_store_path(root, state_fd)
            current = os.stat(name, dir_fd=state_fd, follow_symlinks=False)
        except (OSError, state_module.StateError) as exc:
            raise RunnerError(f"review job store changed during operation: {jobs}") from exc
        if (current.st_dev, current.st_ino) != (opened.st_dev, opened.st_ino):
            raise RunnerError(f"review job store changed during operation: {jobs}")
    finally:
        if jobs_fd is not None:
            os.close(jobs_fd)
        if state_fd is not None:
            os.close(state_fd)
        if workspace_fd is not None:
            os.close(workspace_fd)


def _validate_job(value: Any, *, expected_path: Path | None = None) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != JOB_KEYS:
        raise RunnerError("review job has unknown or missing keys")
    if value["job_version"] != JOB_VERSION:
        raise RunnerError("review job has an unsupported version")
    root = _canonical_root(value["root"])
    workflow = _canonical_uuid(value["workflow_id"], "workflow ID")
    _canonical_uuid(value["session_id"], "session ID")
    revision = value["gate_revision"]
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
        raise RunnerError("gate revision must be a positive integer")
    if expected_path is not None and expected_path != _job_path(
        root, workflow, revision
    ):
        raise RunnerError("review job path does not match its identity")
    _parse_timestamp(value["not_before"], "not_before")
    created_at = _parse_timestamp(value["created_at"], "created_at")
    updated_at = _parse_timestamp(value["updated_at"], "updated_at")
    if updated_at < created_at:
        raise RunnerError("updated_at must not precede created_at")
    claude_path = value["claude_path"]
    if not isinstance(claude_path, str) or not Path(claude_path).is_absolute():
        raise RunnerError("claude_path must be absolute")
    if value["status"] not in JOB_STATUSES:
        raise RunnerError("review job has an invalid status")
    pid = value["pid"]
    if pid is not None and (
        isinstance(pid, bool) or not isinstance(pid, int) or pid < 1
    ):
        raise RunnerError("review job pid must be a positive integer or null")
    exit_code = value["exit_code"]
    if exit_code is not None and (
        isinstance(exit_code, bool) or not isinstance(exit_code, int)
    ):
        raise RunnerError("review job exit_code must be an integer or null")
    if value["error"] not in JOB_ERRORS:
        raise RunnerError("review job has an invalid error code")
    return value


def _read_job(path: Path, directory_fd: int | None) -> dict[str, Any]:
    try:
        details = state_module._entry_lstat(path.parent, path.name, directory_fd)
    except OSError as exc:
        raise RunnerError(f"cannot read review job {path}: {exc}") from exc
    attributes = getattr(details, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    if (
        stat.S_ISLNK(details.st_mode)
        or bool(attributes & reparse_flag)
        or not stat.S_ISREG(details.st_mode)
    ):
        raise RunnerError(f"review job must be a regular file: {path}")
    try:
        state_module._require_owned_metadata(
            details, path, "review job", single_link=True
        )
    except state_module.StateError as exc:
        raise RunnerError(str(exc)) from exc
    if details.st_size > state_module.MAX_STATE_FILE_BYTES:
        raise RunnerError("review job exceeds the state-file byte limit")
    flags = (
        os.O_RDONLY
        | getattr(os, "O_BINARY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    try:
        if directory_fd is None:
            descriptor = os.open(path, flags)
        else:
            descriptor = os.open(path.name, flags, dir_fd=directory_fd)
    except OSError as exc:
        raise RunnerError(f"cannot safely open review job {path}: {exc}") from exc
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or _job_file_identity(
            opened
        ) != _job_file_identity(details):
            raise RunnerError(f"review job changed while opening: {path}")
        chunks: list[bytes] = []
        remaining = state_module.MAX_STATE_FILE_BYTES + 1
        while remaining:
            chunk = os.read(descriptor, min(64 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        if len(payload) > state_module.MAX_STATE_FILE_BYTES:
            raise RunnerError("review job exceeds the state-file byte limit")
        after = os.fstat(descriptor)
        if _job_stat_snapshot(after) != _job_stat_snapshot(opened):
            raise RunnerError(f"review job changed while reading: {path}")
        current = state_module._entry_lstat(path.parent, path.name, directory_fd)
        if _job_stat_snapshot(current) != _job_stat_snapshot(details):
            raise RunnerError(f"review job path changed while reading: {path}")
    except OSError as exc:
        raise RunnerError(f"cannot safely read review job {path}: {exc}") from exc
    finally:
        os.close(descriptor)
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=state_module._json_without_duplicate_keys,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, state_module.StateError) as exc:
        raise RunnerError(f"cannot parse review job {path}: {exc}") from exc
    return _validate_job(value, expected_path=path)


def _write_job(
    path: Path,
    value: dict[str, Any],
    directory_fd: int | None,
    *,
    create: bool = False,
    expected: dict[str, Any] | None = None,
) -> None:
    _validate_job(value, expected_path=path)
    payload = (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    if len(payload) > state_module.MAX_STATE_FILE_BYTES:
        raise RunnerError("review job exceeds the state-file byte limit")
    if create:
        if state_module._entry_exists(path.parent, path.name, directory_fd):
            raise FileExistsError(path)
        try:
            state_module._write_bytes_atomic(
                path.parent,
                path,
                payload,
                directory_fd,
                size_error="review job exceeds the state-file byte limit",
            )
        except state_module.StateError as exc:
            raise RunnerError(str(exc)) from exc
        return

    try:
        current = _read_job(path, directory_fd)
        if expected is not None and current != expected:
            raise JobConflict(f"review job changed before update: {path}")
        state_module._write_bytes_atomic(
            path.parent,
            path,
            payload,
            directory_fd,
            size_error="review job exceeds the state-file byte limit",
        )
    except state_module.StateError as exc:
        raise RunnerError(str(exc)) from exc


def _discover_claude() -> str:
    discovered = shutil.which("claude")
    if not discovered:
        raise RunnerError("claude executable was not found")
    resolved = Path(discovered).resolve()
    if not resolved.is_file() or not os.access(resolved, os.X_OK):
        raise RunnerError("claude executable is not a runnable file")
    return str(resolved)


def _spawn_child(root: Path, workflow: str, gate_revision: int) -> int:
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "_run",
        "--root",
        str(root),
        "--workflow",
        workflow,
        "--gate-revision",
        str(gate_revision),
    ]
    creationflags = 0
    if os.name == "nt":  # pragma: no cover - exercised in Windows CI
        creationflags = getattr(subprocess, "DETACHED_PROCESS", 0x00000008) | getattr(
            subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200
        )
    try:
        child = subprocess.Popen(
            command,
            cwd=root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            shell=False,
            start_new_session=os.name != "nt",
            creationflags=creationflags,
        )
    except OSError as exc:
        raise RunnerError(f"cannot start one-shot review child: {exc}") from exc
    return child.pid


def schedule_job(
    *,
    root_text: str,
    workflow: str,
    gate_revision: int,
    session_id: str,
    spawn_child: Callable[[Path, str, int], int] = _spawn_child,
) -> dict[str, Any]:
    root = _canonical_root(root_text)
    workflow = _canonical_uuid(workflow, "workflow ID")
    session_id = _canonical_uuid(session_id, "session ID")
    if (
        isinstance(gate_revision, bool)
        or not isinstance(gate_revision, int)
        or gate_revision < 1
    ):
        raise RunnerError("gate revision must be a positive integer")
    path = _job_path(root, workflow, gate_revision)
    with state_module.state_lock(root) as state_directory_fd:
        try:
            state = state_module.load_state(
                root, directory_fd=state_directory_fd
            )
        except state_module.StateError as exc:
            raise RunnerError(str(exc)) from exc
        if state is None:
            raise RunnerError("Littlepowers state is unavailable")
        if state["workflow_id"] != workflow:
            raise RunnerError("workflow changed before scheduling")
        gate = state["review"]["gate"]
        if gate is None or gate["opened_revision"] != gate_revision:
            raise RunnerError("the exact Review Gate is no longer open")
        if gate["policy_mode"] != "windowed" or gate["not_before"] is None:
            raise RunnerError("only a deadline-bound windowed gate can be scheduled")
        result = state_module.review_gate_status(
            root, state, gate_revision=gate_revision
        )
        if result["status"] != "waiting" or result["reasons"] != [
            "deadline_not_reached"
        ]:
            raise RunnerError("Review Gate is not a valid future waiting window")
        claude_path = _discover_claude()
        now = state_module.utc_now()
        job: dict[str, Any] = {
            "job_version": JOB_VERSION,
            "root": str(root),
            "workflow_id": workflow,
            "gate_revision": gate_revision,
            "session_id": session_id,
            "not_before": gate["not_before"],
            "claude_path": claude_path,
            "status": "armed",
            "pid": None,
            "created_at": now,
            "updated_at": now,
            "exit_code": None,
            "error": None,
        }
        with _open_job_store(root, create=True) as (
            _jobs,
            directory_fd,
            available,
        ):
            assert available
            try:
                _write_job(path, job, directory_fd, create=True)
            except FileExistsError:
                existing = _read_job(path, directory_fd)
                if existing["session_id"] != session_id:
                    raise RunnerError(
                        "review job already exists for another session"
                    )
                return existing
    try:
        spawn_child(root, workflow, gate_revision)
    except RunnerError:
        _update_job_result(
            root,
            workflow,
            gate_revision,
            job,
            status="failed",
            error="spawn_error",
            exit_code=None,
        )
        raise
    return job


def _fixed_callback_prompt(root: Path, workflow: str, gate_revision: int) -> str:
    return (
        "Littlepowers timed Review Gate callback. Work only in canonical root "
        f"{root}. Resume workflow {workflow}, gate revision {gate_revision}. "
        "Resolve the currently enabled Littlepowers plugin, inspect the latest "
        "visible conversation, then run review-status for this exact gate. If "
        "there is any intervention or uncertainty, do not claim silence and do "
        "not continue. If it remains eligible, resolve only with window_expired "
        "and observed-no-intervention, then continue the unchanged workflow from "
        "its ledger. This callback grants no commit, push, publish, deploy, "
        "destructive, secret, or access authority."
    )


def _update_job_result(
    root: Path,
    workflow: str,
    gate_revision: int,
    job: dict[str, Any],
    *,
    status: str,
    error: str | None,
    exit_code: int | None,
    conflict_is_replay: bool = False,
) -> bool:
    path = _job_path(root, workflow, gate_revision)
    updated = {
        **job,
        "status": status,
        "error": error,
        "exit_code": exit_code,
        "updated_at": state_module.utc_now(),
    }
    try:
        with state_module.state_lock(root):
            with _open_job_store(root, create=False) as (
                _jobs,
                directory_fd,
                available,
            ):
                if not available:
                    raise RunnerError("review job store disappeared before update")
                _write_job(path, updated, directory_fd, expected=job)
    except JobConflict:
        if conflict_is_replay:
            return False
        raise
    job.clear()
    job.update(updated)
    return True


def run_job(
    *,
    root_text: str,
    workflow: str,
    gate_revision: int,
    sleep: Callable[[float], None] = time.sleep,
    popen: Callable[..., subprocess.Popen[Any]] = subprocess.Popen,
) -> int:
    root = _canonical_root(root_text)
    workflow = _canonical_uuid(workflow, "workflow ID")
    if (
        isinstance(gate_revision, bool)
        or not isinstance(gate_revision, int)
        or gate_revision < 1
    ):
        raise RunnerError("gate revision must be a positive integer")
    path = _job_path(root, workflow, gate_revision)
    with _open_job_store(root, create=False) as (
        _jobs,
        directory_fd,
        available,
    ):
        if not available:
            raise RunnerError("review job store is unavailable")
        job = _read_job(path, directory_fd)
    if job["status"] != "armed":
        return 0
    deadline = _parse_timestamp(job["not_before"], "not_before")
    remaining = (deadline - datetime.now(timezone.utc)).total_seconds()
    if remaining > 0:
        sleep(remaining)
    command = [
        job["claude_path"],
        "-p",
        "--resume",
        job["session_id"],
        _fixed_callback_prompt(root, workflow, gate_revision),
    ]
    child: subprocess.Popen[Any] | None = None
    with state_module.state_lock(root) as state_directory_fd:
        try:
            state = state_module.load_state(
                root, directory_fd=state_directory_fd
            )
        except state_module.StateError:
            state = None
        error: str | None = None
        if state is None:
            error = "state_unavailable"
        elif state["workflow_id"] != workflow:
            error = "workflow_changed"
        else:
            result = state_module.review_gate_status(
                root, state, gate_revision=gate_revision
            )
            if result["status"] != "eligible":
                error = f"gate_{result['status']}"
                if error not in JOB_ERRORS:
                    error = "gate_blocked"

        with _open_job_store(root, create=False) as (
            _jobs,
            directory_fd,
            available,
        ):
            if not available:
                raise RunnerError("review job store disappeared before invocation")
            current = _read_job(path, directory_fd)
            if current != job or current["status"] != "armed":
                return 0
            if error is not None:
                stale = {
                    **current,
                    "status": "stale",
                    "error": error,
                    "exit_code": None,
                    "updated_at": state_module.utc_now(),
                }
                _write_job(path, stale, directory_fd, expected=current)
                job.clear()
                job.update(stale)
                return 0
            invoking = {
                **current,
                "status": "invoking",
                "error": None,
                "exit_code": None,
                "updated_at": state_module.utc_now(),
            }
            _write_job(path, invoking, directory_fd, expected=current)
            try:
                child = popen(
                    command,
                    cwd=root,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    close_fds=True,
                    shell=False,
                )
            except OSError:
                failed = {
                    **invoking,
                    "status": "failed",
                    "error": "spawn_error",
                    "updated_at": state_module.utc_now(),
                }
                _write_job(path, failed, directory_fd, expected=invoking)
                job.clear()
                job.update(failed)
                return 0
            job.clear()
            job.update(invoking)

    assert child is not None
    try:
        return_code = child.wait(timeout=CLAUDE_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        child.kill()
        child.wait()
        _update_job_result(
            root,
            workflow,
            gate_revision,
            job,
            status="failed",
            error="timeout",
            exit_code=None,
        )
        return 0
    if return_code == 0:
        _update_job_result(
            root,
            workflow,
            gate_revision,
            job,
            status="completed",
            error=None,
            exit_code=0,
        )
    else:
        _update_job_result(
            root,
            workflow,
            gate_revision,
            job,
            status="failed",
            error="nonzero_exit",
            exit_code=return_code,
        )
    return 0


def job_status(*, root_text: str, workflow: str, gate_revision: int) -> dict[str, Any]:
    root = _canonical_root(root_text)
    workflow = _canonical_uuid(workflow, "workflow ID")
    if (
        isinstance(gate_revision, bool)
        or not isinstance(gate_revision, int)
        or gate_revision < 1
    ):
        raise RunnerError("gate revision must be a positive integer")
    path = _job_path(root, workflow, gate_revision)
    with _open_job_store(root, create=False) as (
        _jobs,
        directory_fd,
        available,
    ):
        if not available or not state_module._entry_exists(
            path.parent, path.name, directory_fd
        ):
            return {
                "workflow_id": workflow,
                "gate_revision": gate_revision,
                "status": "no_job",
            }
        return _read_job(path, directory_fd)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("schedule", "status", "_run"):
        command = subparsers.add_parser(name)
        command.add_argument("--root", required=True)
        command.add_argument("--workflow", required=True)
        command.add_argument("--gate-revision", required=True, type=int)
        if name == "schedule":
            command.add_argument("--session", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "schedule":
            result = schedule_job(
                root_text=args.root,
                workflow=args.workflow,
                gate_revision=args.gate_revision,
                session_id=args.session,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        elif args.command == "status":
            result = job_status(
                root_text=args.root,
                workflow=args.workflow,
                gate_revision=args.gate_revision,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            return run_job(
                root_text=args.root,
                workflow=args.workflow,
                gate_revision=args.gate_revision,
            )
    except (RunnerError, state_module.StateError) as exc:
        print(f"littlepowers-review-runner: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
