from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pron_scoring import ScoringConfig, score_pronunciation_alignment


class OptionalSchwaSonorantSequenceRuleTest(unittest.TestCase):
    def test_inserted_l_realizes_optional_l_after_vowel_substitution(self) -> None:
        result = score_pronunciation_alignment(self._alignment("(ə)l", "ɪ", "l"))

        self.assertEqual(
            self._compact(result["events"]),
            [
                {
                    "kind": "extra_heard",
                    "status": "insertion",
                    "display_status": "insertion",
                    "target_phone": None,
                    "target_index": None,
                    "heard_phone": "ɪ",
                    "wper_cost": ScoringConfig.default_insertion_cost,
                    "quality": 0.2,
                    "rule": "optional_schwa_sonorant_sequence",
                },
                {
                    "kind": "accepted_realization",
                    "status": "insertion",
                    "display_status": "accepted",
                    "target_phone": "(ə)l",
                    "target_index": 0,
                    "heard_phone": "l",
                    "wper_cost": 0.0,
                    "quality": 1.0,
                    "rule": "optional_schwa_sonorant_sequence",
                },
            ],
        )
        self.assertEqual(
            self._compact(result["diagnostic_events"]),
            [
                {
                    "kind": "heard_substitution",
                    "status": "substitution",
                    "target_phone": "(ə)l",
                    "target_index": 0,
                    "heard_phone": "ɪ",
                    "wper_cost": 1.0,
                    "quality": 0.0,
                    "rule": "default_substitution",
                },
                {
                    "kind": "extra_heard",
                    "status": "insertion",
                    "target_phone": None,
                    "target_index": None,
                    "heard_phone": "l",
                    "wper_cost": ScoringConfig.default_insertion_cost,
                    "quality": 0.2,
                    "rule": "default_insertion",
                },
            ],
        )

    def test_inserted_n_realizes_optional_n_after_vowel_substitution(self) -> None:
        result = score_pronunciation_alignment(self._alignment("(ə)n", "ɪ", "n"))

        self.assertEqual(result["events"][0]["kind"], "extra_heard")
        self.assertEqual(result["events"][0]["heard_phone"], "ɪ")
        self.assertEqual(result["events"][0]["wper_cost"], ScoringConfig.default_insertion_cost)
        self.assertEqual(result["events"][1]["kind"], "accepted_realization")
        self.assertEqual(result["events"][1]["target_phone"], "(ə)n")
        self.assertEqual(result["events"][1]["heard_phone"], "n")
        self.assertEqual(result["events"][1]["wper_cost"], 0.0)
        self.assertEqual(result["diagnostic_events"][0]["target_phone"], "(ə)n")
        self.assertEqual(result["diagnostic_events"][0]["heard_phone"], "ɪ")
        self.assertEqual(result["diagnostic_events"][1]["heard_phone"], "n")

    @staticmethod
    def _alignment(target_phone: str, substituted_phone: str, inserted_phone: str) -> dict:
        return {
            "phones": [
                {
                    "phone": target_phone,
                    "status": "substitution",
                    "best_phone": substituted_phone,
                    "target_prob": 0.01,
                    "start_frame": 10,
                    "end_frame": 12,
                }
            ],
            "insertions": [
                {
                    "phone": inserted_phone,
                    "start_frame": 13,
                    "end_frame": 14,
                }
            ],
        }

    @staticmethod
    def _compact(events: list[dict]) -> list[dict]:
        fields = (
            "kind",
            "status",
            "display_status",
            "target_phone",
            "target_index",
            "heard_phone",
            "wper_cost",
            "quality",
            "rule",
        )
        return [{field: event[field] for field in fields if field in event} for event in events]


if __name__ == "__main__":
    unittest.main()
