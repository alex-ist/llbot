import concurrent.futures
import json
import logging
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

# Unit tests must not initialize the production log or any external clients.
with patch.dict(sys.modules, {"botlog": SimpleNamespace(logger=logging.getLogger("xvibe-test"))}):
    import xvibe
import xvibe_worker


FAKE_TTS = '''
import json
import os
from pathlib import Path
import time

print("diagnostic during TTS import")
os.write(1, b"native diagnostic during TTS import\\n")

def record(event, **values):
    with open(os.environ["XVIBE_TEST_EVENTS"], "a", encoding="utf-8") as output:
        output.write(json.dumps(dict(event=event, pid=os.getpid(), **values)) + "\\n")

class Audio:
    def __init__(self, text):
        self.text = text
    def numpy(self):
        return "writefail" if self.text == "WRITEFAIL" else [0.0, 0.1]

class RussianTTS:
    sample_rate = 24000
    def __init__(self):
        print("diagnostic during model load")
        record("load")
    def generate(self, text, voice):
        print("diagnostic during generation")
        record("start", text=text, voice=voice)
        if text == "CRASH":
            os._exit(23)
        if text == "CRASH_ONCE":
            marker = Path(os.environ["XVIBE_TEST_EVENTS"] + ".crash")
            if not marker.exists():
                marker.touch()
                os._exit(23)
        if text == "FAIL":
            raise ValueError("fake synthesis failure")
        if text == "SLOW":
            time.sleep(0.5)
        else:
            time.sleep(0.01)
        record("finish", text=text)
        return Audio(text)
'''
FAKE_SOUNDFILE = '''
def write(path, audio, sample_rate):
    with open(path, "wb") as output:
        output.write(b"RIFF")
    if audio == "writefail":
        raise OSError("fake output failure")
'''


class XvibeSpeechTest(unittest.TestCase):
    def test_adds_period_when_example_has_no_punctuation(self):
        self.assertEqual(xvibe.add_final_period("Пример без точки"), "Пример без точки.")
        self.assertEqual(xvibe.add_final_period("  Пример без точки  "), "Пример без точки.")

    def test_preserves_existing_punctuation(self):
        for text in ("Это вопрос?", "Отлично!", "Продолжение…", "Перечень:"):
            self.assertEqual(xvibe.add_final_period(text), text)

    def test_generates_wav_atomically(self):
        model = MagicMock()
        model.sample_rate = 24000
        model.generate.return_value.numpy.return_value = [0.0, 0.1]

        def write(path, *_args, **_kwargs):
            with open(path, "wb") as output:
                output.write(b"RIFF")

        with tempfile.TemporaryDirectory() as directory:
            output_path = os.path.join(directory, "audio.wav")
            with patch.dict(sys.modules, {"soundfile": SimpleNamespace(write=write)}):
                xvibe_worker._generate_speech(model, "Привет", output_path, "male_deep")
            self.assertEqual(Path(output_path).read_bytes(), b"RIFF")
            self.assertFalse(Path(output_path + ".tmp.wav").exists())
            model.generate.assert_called_once_with("Привет", voice="male_deep")

    def test_reuses_cached_audio_without_starting_a_worker(self):
        with tempfile.TemporaryDirectory() as directory:
            output_path = os.path.join(directory, "audio.wav")
            Path(output_path).write_bytes(b"cached")
            with patch.object(xvibe, "_get_worker") as get_worker:
                xvibe._generate_speech("Привет", output_path)
            get_worker.assert_not_called()
            self.assertEqual(Path(output_path).read_bytes(), b"cached")


class XvibeProcessTest(unittest.TestCase):
    def setUp(self):
        xvibe.shutdown_xvibe()
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)
        fake = self.directory / "fake"
        (fake / "xvibe_pocket_tts").mkdir(parents=True)
        (fake / "xvibe_pocket_tts" / "__init__.py").write_text(FAKE_TTS)
        (fake / "soundfile.py").write_text(FAKE_SOUNDFILE)
        (fake / "botlog.py").write_text("import logging\nlogger = logging.getLogger('fake-botlog')\n")
        self.events_path = self.directory / "events.jsonl"
        self.environment = patch.dict(os.environ, {
            "PYTHONPATH": str(fake),
            "XVIBE_TEST_EVENTS": str(self.events_path),
            "PYTHONDONTWRITEBYTECODE": "1",
        })
        self.environment.start()
        self.idle = patch.object(xvibe, "WORKER_IDLE_TIMEOUT_SECONDS", 5)
        self.response = patch.object(xvibe, "WORKER_RESPONSE_TIMEOUT_SECONDS", 5)
        self.idle.start()
        self.response.start()

    def tearDown(self):
        xvibe.shutdown_xvibe()
        self.response.stop()
        self.idle.stop()
        self.environment.stop()
        self.temporary.cleanup()

    def events(self, kind=None):
        if not self.events_path.exists():
            return []
        records = [json.loads(line) for line in self.events_path.read_text().splitlines()]
        return records if kind is None else [r for r in records if r["event"] == kind]

    def output(self, name="audio.wav"):
        return str(self.directory / name)

    def test_protocol_survives_library_stdout_and_unicode(self):
        text = "Привет!\nВторая строка."
        with patch.object(xvibe, "XVIBE_VOICE", "female_silky"):
            xvibe._generate_speech(text, self.output("файл с пробелами.wav"))
        self.assertEqual(self.events("start")[0]["text"], text)
        self.assertEqual(self.events("start")[0]["voice"], "female_silky")
        self.assertNotIn("xvibe_pocket_tts", sys.modules)
        self.assertNotIn("soundfile", sys.modules)

    def test_model_is_reused_between_requests(self):
        xvibe._generate_speech("Один", self.output("one.wav"))
        first = xvibe._worker
        xvibe._generate_speech("Два", self.output("two.wav"))
        self.assertIs(xvibe._worker, first)
        self.assertEqual(len(self.events("load")), 1)
        self.assertEqual(len(self.events("finish")), 2)

    def test_worker_exits_after_idle_and_restarts_on_next_request(self):
        with patch.object(xvibe, "WORKER_IDLE_TIMEOUT_SECONDS", 0.2):
            xvibe._generate_speech("Один", self.output("one.wav"))
            first = xvibe._worker
            self.assertEqual(first.wait(timeout=5), 0)
            xvibe._generate_speech("Два", self.output("two.wav"))
            self.assertNotEqual(xvibe._worker.pid, first.pid)
            self.assertEqual(len(self.events("load")), 2)

    def test_idle_interval_restarts_after_each_completed_request(self):
        with patch.object(xvibe, "WORKER_IDLE_TIMEOUT_SECONDS", 0.6):
            xvibe._generate_speech("Один", self.output("one.wav"))
            first = xvibe._worker
            time.sleep(0.35)
            xvibe._generate_speech("Два", self.output("two.wav"))
            time.sleep(0.35)
            self.assertIsNone(first.poll())
            self.assertIs(xvibe._worker, first)
            self.assertEqual(first.wait(timeout=5), 0)

    def test_idle_timer_does_not_interrupt_active_synthesis(self):
        with patch.object(xvibe, "WORKER_IDLE_TIMEOUT_SECONDS", 0.1):
            xvibe._generate_speech("SLOW", self.output())
            self.assertEqual(Path(self.output()).read_bytes(), b"RIFF")
            self.assertEqual(xvibe._worker.wait(timeout=5), 0)

    def test_cached_audio_does_not_contact_an_existing_worker(self):
        xvibe._generate_speech("Первый", self.output())
        with patch.object(xvibe, "_request_speech") as request:
            xvibe._generate_speech("Кеш", self.output())
        request.assert_not_called()
        self.assertEqual(len(self.events("start")), 1)

    def test_concurrent_requests_are_serialized(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(xvibe._generate_speech, str(i), self.output(f"{i}.wav")) for i in range(4)]
            for future in futures:
                future.result(timeout=5)
        events = [r["event"] for r in self.events() if r["event"] != "load"]
        self.assertEqual(events, ["start", "finish"] * 4)
        self.assertEqual(len(self.events("load")), 1)

    def test_concurrent_requests_for_same_file_generate_once(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(xvibe._generate_speech, "Один", self.output()) for _ in range(4)]
            for future in futures:
                future.result(timeout=5)
        self.assertEqual(len(self.events("start")), 1)

    def test_synthesis_error_is_reported_without_retry_and_worker_survives(self):
        with self.assertRaisesRegex(RuntimeError, "fake synthesis failure"):
            xvibe._generate_speech("FAIL", self.output())
        self.assertFalse(Path(self.output()).exists())
        worker = xvibe._worker
        xvibe._generate_speech("Хорошо", self.output())
        self.assertIs(xvibe._worker, worker)
        self.assertEqual(len(self.events("load")), 1)
        self.assertEqual(len(self.events("start")), 2)

    def test_failed_write_leaves_neither_partial_output_nor_temp_file(self):
        with self.assertRaisesRegex(RuntimeError, "fake output failure"):
            xvibe._generate_speech("WRITEFAIL", self.output())
        self.assertFalse(Path(self.output()).exists())
        self.assertFalse(Path(self.output() + ".tmp.wav").exists())

    def test_worker_crash_is_retried_once(self):
        xvibe._generate_speech("CRASH_ONCE", self.output())
        self.assertEqual(Path(self.output()).read_bytes(), b"RIFF")
        self.assertEqual(len(self.events("load")), 2)

    def test_repeated_worker_crash_returns_error_and_cleans_up(self):
        with self.assertRaisesRegex(RuntimeError, "disconnected"):
            xvibe._generate_speech("CRASH", self.output())
        self.assertIsNone(xvibe._worker)
        self.assertEqual(len(self.events("load")), 2)

    def test_worker_timeout_terminates_process(self):
        xvibe._generate_speech("Разогрев", self.output("warm.wav"))
        worker = xvibe._worker
        with patch.object(xvibe, "WORKER_RESPONSE_TIMEOUT_SECONDS", 0.05):
            with self.assertRaises(TimeoutError):
                xvibe._generate_speech("SLOW", self.output())
        self.assertIsNone(xvibe._worker)
        self.assertIsNotNone(worker.poll())
        self.assertFalse(Path(self.output()).exists())

    def test_exit_between_poll_and_write_is_recovered(self):
        request = xvibe._request_speech
        calls = 0
        def exit_first(process, *args):
            nonlocal calls
            calls += 1
            if calls == 1:
                process.terminate()
                process.wait(timeout=5)
            return request(process, *args)
        with patch.object(xvibe, "_request_speech", side_effect=exit_first):
            xvibe._generate_speech("Граница таймера", self.output())
        self.assertEqual(calls, 2)
        self.assertEqual(Path(self.output()).read_bytes(), b"RIFF")

    def test_explicit_shutdown_releases_worker(self):
        xvibe._generate_speech("Один", self.output())
        worker = xvibe._worker
        xvibe.shutdown_xvibe()
        self.assertIsNone(xvibe._worker)
        self.assertIsNotNone(worker.poll())

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux parent-death signal")
    def test_worker_stops_if_bot_process_dies(self):
        environment = dict(os.environ)
        environment["PYTHONPATH"] += os.pathsep + str(Path(xvibe.__file__).parent)
        script = (
            "import os, sys, xvibe\n"
            "xvibe._generate_speech('Parent exit', sys.argv[1])\n"
            "print(xvibe._worker.pid, flush=True)\n"
            "os._exit(0)\n"
        )
        parent = subprocess.run(
            [sys.executable, "-c", script, self.output()], env=environment,
            capture_output=True, text=True, timeout=5, check=True,
        )
        pid = int(parent.stdout.strip())
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            try:
                status = Path(f"/proc/{pid}/status").read_text()
            except FileNotFoundError:
                return
            if "State:\tZ" in status:
                return
            time.sleep(0.02)
        self.fail("Synthesis worker remained running after its parent exited")


if __name__ == "__main__":
    unittest.main()
