"""Explicit synthetic host harness, NOT an installed host adapter or runtime service.

Only caller-supplied synthetic awaitables and paths. No browser/network/model calls.
The production helper never imports this file. Real hosts must supply equivalent
cancellation/timeout/handle semantics or report degraded capability.
"""
import asyncio
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import littlepowers_efficiency as eff


def atomic_save(path, value):
    """Root-owned normal boundary example; caller owns authorization and isolation."""
    path = Path(path)
    payload = eff.canonical(value).encode('utf-8')
    fd, temporary = tempfile.mkstemp(prefix='.candidate-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if Path(temporary).read_bytes() != payload:
            raise ValueError('saved evidence integrity failure')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return dict(ref=path.name, sha256='sha256:' + hashlib.sha256(payload).hexdigest(),
                saved=True, upstream_complete=True)


def verify_receipt(path, receipt):
    """Explicit already-authorized path; never opens receipt.ref as a path."""
    actual = 'sha256:' + hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if actual != receipt['sha256']:
        raise ValueError('evidence changed')
    return dict(receipt)


async def independent_reads(readers):
    """One decision, independent synthetic readers only; every exit is retained."""
    values = await asyncio.gather(*(reader() for reader in readers), return_exceptions=True)
    return [dict(index=i, exit_status=1, error=type(v).__name__) if isinstance(v, BaseException)
            else dict(index=i, exit_status=0, value=v) for i, v in enumerate(values)]


async def bounded_batch(observe, handle, *, duration_ms, observation_timeout_ms,
                        report_after_ms, interval_ms, cancel, capabilities):
    """Uses actual asyncio waits/cancel; synthetic tools must cooperate with cancel.

    An uninterruptible blocking tool is NOT supported by these capabilities.
    Adapter must instead use the host's bounded cancellable process/task API.
    """
    start = int(time.monotonic() * 1000)
    deadline, report_deadline = start + duration_ms, start + report_after_ms
    calls = 0
    while True:
        proposal = eff.batch_decision(now_ms=int(time.monotonic() * 1000), deadline_ms=deadline,
            report_deadline_ms=report_deadline, observation_timeout_ms=observation_timeout_ms,
            cancelled=cancel.is_set(), capabilities=capabilities)
        if proposal['action'] != 'observe':
            return dict(proposal, calls=calls)
        calls += 1
        running = asyncio.create_task(observe(handle))
        cancellation = asyncio.create_task(cancel.wait())
        try:
            done, _ = await asyncio.wait({running, cancellation}, timeout=proposal['timeout_ms'] / 1000,
                                         return_when=asyncio.FIRST_COMPLETED)
            if cancellation in done:
                return dict(action='return', reason='cancelled', calls=calls)
            if running not in done:
                now = int(time.monotonic() * 1000)
                reason = ('periodic_report_due' if now >= report_deadline else
                          'batch_deadline' if now >= deadline else 'observation_timeout')
                return dict(action='return', reason=reason, result='UNKNOWN', calls=calls)
            try:
                result = running.result()
            except Exception as exc:
                return dict(action='return', reason='collection_error', error=type(exc).__name__, calls=calls)
            if result['action'] != 'continue':
                return dict(action='return', reason='event', event=result, calls=calls)
        finally:
            for task in (running, cancellation):
                if not task.done():
                    task.cancel()
            await asyncio.gather(running, cancellation, return_exceptions=True)
        # A periodic report or cancellation also bounds the inter-sample wait.
        remaining = max(0, min(deadline, report_deadline) - int(time.monotonic() * 1000))
        try:
            await asyncio.wait_for(cancel.wait(), timeout=min(interval_ms, remaining) / 1000)
        except asyncio.TimeoutError:
            pass
