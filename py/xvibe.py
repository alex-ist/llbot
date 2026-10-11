import asyncio
import atexit
import contextlib
import json
import os
from pathlib import Path
import select
import subprocess
import sys
import threading
import unicodedata

from botlog import logger
from xvibe_worker import DEFAULT_IDLE_TIMEOUT_SECONDS


XVIBE_VOICE = os.getenv("XVIBE_VOICE", "male_deep")
WORKER_IDLE_TIMEOUT_SECONDS = DEFAULT_IDLE_TIMEOUT_SECONDS
# Bound a stalled load/synthesis independently of the idle timeout.
WORKER_RESPONSE_TIMEOUT_SECONDS = 600

_worker = None
_tts_lock = threading.Lock()


class _WorkerDisconnected(Exception):
    pass


def add_final_period(text: str) -> str:
    text = text.strip()
    if not text or unicodedata.category(text[-1]).startswith("P"):
        return text
    return f"{text}."


def _reap_worker(process) -> None:
    returncode = process.wait()
    logger.info("xVibe worker exited: pid=%s, status=%s", process.pid, returncode)


def _stop_worker() -> None:
    """Caller holds _tts_lock; never leave an unresponsive worker running."""
    global _worker
    process, _worker = _worker, None
    if process is None:
        return
    try:
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
    finally:
        for pipe in (process.stdin, process.stdout):
            # A buffered flush on close can fail after an idle exit/crash.
            with contextlib.suppress(OSError):
                pipe.close()


def _get_worker():
    global _worker
    if _worker is not None and _worker.poll() is not None:
        _stop_worker()
    if _worker is None:
        command = [
            sys.executable,
            "-u",
            str(Path(__file__).with_name("xvibe_worker.py")),
            "--idle-timeout",
            str(WORKER_IDLE_TIMEOUT_SECONDS),
            "--parent-pid",
            str(os.getpid()),
        ]
        _worker = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            # Keep model diagnostics away from the response pipe.
            stderr=None,
            text=True,
            encoding="utf-8",
            close_fds=True,
        )
        threading.Thread(target=_reap_worker, args=(_worker,), daemon=True).start()
        logger.info("Started xVibe worker: pid=%s", _worker.pid)
    return _worker


def _request_speech(process, text: str, file_name: str) -> None:
    request = {"text": text, "file_name": file_name, "voice": XVIBE_VOICE}
    process.stdin.write(json.dumps(request, ensure_ascii=False) + "\n")
    process.stdin.flush()
    readable, _, _ = select.select(
        [process.stdout], [], [], WORKER_RESPONSE_TIMEOUT_SECONDS
    )
    if not readable:
        raise TimeoutError("xVibe worker timed out loading or generating speech")
    response = process.stdout.readline()
    if not response:
        raise _WorkerDisconnected("xVibe worker closed its response pipe")
    result = json.loads(response)
    if not isinstance(result, dict) or not isinstance(result.get("ok"), bool):
        raise ValueError("Invalid xVibe worker response")
    if not result["ok"]:
        raise RuntimeError(f"xVibe synthesis failed: {result.get('error', 'unknown error')}")
    if not os.path.isfile(file_name):
        raise RuntimeError("xVibe worker completed without producing an audio file")


def _generate_speech(text: str, file_name: str) -> None:
    # One request at a time. Cached files neither start nor keep a worker alive.
    with _tts_lock:
        if os.path.isfile(file_name):
            return
        for attempt in range(2):
            process = _get_worker()
            try:
                _request_speech(process, text, file_name)
                return
            except (BrokenPipeError, ConnectionResetError, _WorkerDisconnected) as exc:
                _stop_worker()
                # The idle deadline can expire between poll() and the write.
                # Atomic, cached outputs make a single retry safe.
                if attempt:
                    raise RuntimeError("xVibe worker disconnected during synthesis") from exc
            except (TimeoutError, ValueError):
                _stop_worker()
                raise


def shutdown_xvibe() -> None:
    with _tts_lock:
        _stop_worker()


async def xvibe_speech(text: str, file_name: str) -> None:
    logger.info(f'Generate Russian audio with xVibePocketTTS: "{text}"')
    await asyncio.to_thread(_generate_speech, text, file_name)


atexit.register(shutdown_xvibe)
