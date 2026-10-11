"""Private xVibe process: newline-delimited JSON over inherited pipes."""

import argparse
import contextlib
import ctypes
import json
import logging
import os
from pathlib import Path
import select
import signal
import sys


DEFAULT_IDLE_TIMEOUT_SECONDS = 15 * 60


def _watch_parent(expected_pid: int) -> None:
    if sys.platform.startswith("linux"):
        # Release model memory even if the bot crashes during synthesis.
        libc = ctypes.CDLL(None, use_errno=True)
        if libc.prctl(1, signal.SIGTERM, 0, 0, 0) != 0:  # PR_SET_PDEATHSIG
            raise OSError(ctypes.get_errno(), "Cannot set parent-death signal")
    if os.getppid() != expected_pid:
        raise SystemExit(0)


def _get_tts():
    from xvibe_pocket_tts import RussianTTS

    logging.info("Loading xVibePocketTTS in synthesis worker")
    return RussianTTS()


def _generate_speech(tts, text: str, file_name: str, voice: str) -> None:
    if os.path.isfile(file_name):
        return
    import soundfile as sf

    audio = tts.generate(text, voice=voice)
    Path(file_name).parent.mkdir(parents=True, exist_ok=True)
    temp_file = f"{file_name}.tmp.wav"
    try:
        sf.write(temp_file, audio.numpy(), tts.sample_rate)
        os.replace(temp_file, file_name)
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def serve(idle_timeout: float) -> None:
    model = None
    responses = os.fdopen(os.dup(sys.stdout.fileno()), "w", encoding="utf-8")
    # Redirect descriptor 1 as well, so native libraries cannot corrupt JSON.
    os.dup2(sys.stderr.fileno(), sys.stdout.fileno())
    # Packages can print during import, loading, or generation. Only our JSON
    # responses go to stdout; all model diagnostics go to systemd stderr.
    with responses, contextlib.redirect_stdout(sys.stderr):
        while True:
            readable, _, _ = select.select([sys.stdin], [], [], idle_timeout)
            if not readable:
                logging.info("xVibe worker idle timeout; exiting")
                return
            request_line = sys.stdin.readline()
            if not request_line:
                return
            try:
                request = json.loads(request_line)
                text, file_name, voice = (
                    request["text"], request["file_name"], request["voice"]
                )
                if not all(isinstance(value, str) for value in (text, file_name, voice)):
                    raise ValueError("Synthesis arguments must be strings")
                if not os.path.isfile(file_name):
                    if model is None:
                        model = _get_tts()
                    _generate_speech(model, text, file_name, voice)
                result = {"ok": True}
            except Exception as exc:
                logging.exception("xVibe synthesis failed")
                result = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            responses.write(json.dumps(result, ensure_ascii=False) + "\n")
            responses.flush()
            # The next select starts a fresh idle interval after the response.
            # An active synthesis is never interrupted by the idle timer.


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--idle-timeout", type=float, default=DEFAULT_IDLE_TIMEOUT_SECONDS)
    parser.add_argument("--parent-pid", type=int, required=True)
    args = parser.parse_args()
    if args.idle_timeout <= 0:
        parser.error("--idle-timeout must be positive")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s xVibe worker %(process)d: %(levelname)s: %(message)s",
    )
    _watch_parent(args.parent_pid)
    serve(args.idle_timeout)


if __name__ == "__main__":
    main()
