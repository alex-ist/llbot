from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Protocol

UNIVERSAL_IPA_PHONES = (
    "sil",
    "i",
    "ɪ",
    "ɛ",
    "æ",
    "ə",
    "ʌ",
    "ɑ",
    "ɔ",
    "ʊ",
    "u",
    "ɚ",
    "ɝ",
    "eɪ",
    "aɪ",
    "aʊ",
    "oʊ",
    "ɔɪ",
    "(ə)n",
    "(ə)l",
    "p",
    "b",
    "t",
    "d",
    "k",
    "ɡ",
    "t̬",
    "tʃ",
    "dʒ",
    "f",
    "v",
    "θ",
    "ð",
    "s",
    "z",
    "ʃ",
    "ʒ",
    "h",
    "m",
    "n",
    "ŋ",
    "l",
    "r",
    "w",
    "j",
)

VOWELS = {
    "i",
    "ɪ",
    "ɛ",
    "æ",
    "ə",
    "ʌ",
    "ɑ",
    "ɔ",
    "ʊ",
    "u",
    "ɚ",
    "ɝ",
    "eɪ",
    "aɪ",
    "aʊ",
    "oʊ",
    "ɔɪ",
}


@dataclass(frozen=True)
class PhoneMetadata:
    phone: str
    index: int
    stress: str | None = None


@dataclass(frozen=True)
class ScoringConfig:
    stressed_vowel_weight: float = 2.0
    secondary_vowel_weight: float = 1.5
    unstressed_vowel_weight: float = 0.6
    vowel_weight_without_stress: float = 1.2
    consonant_weight: float = 1.0
    default_substitution_cost: float = 1.0
    unstressed_vowel_substitution_cost: float = 0.75
    default_deletion_cost: float = 1.0
    default_insertion_cost: float = 0.8
    matched_max_cost: float = 0.25
    matched_low_confidence_prob: float = 0.45
    matched_full_credit_prob: float = 0.75
    matched_best_possible_cost: float = 0.05
    optional_schwa_sequence_cost: float = 0.0


@dataclass(frozen=True)
class EventContext:
    event: dict[str, Any]
    target_index: int | None
    target_phone: str | None
    heard_phone: str | None
    status: str
    metadata: PhoneMetadata | None
    prev_target_phone: str | None
    next_target_phone: str | None
    next_vowel_stress: str | None


@dataclass(frozen=True)
class RuleDecision:
    quality_error: float
    rule: str
    message: str


class ScoringRule(Protocol):
    name: str
    priority: int

    def matches(self, context: EventContext) -> bool:
        ...

    def apply(self, context: EventContext, config: ScoringConfig) -> RuleDecision:
        ...


class TimelineRule(Protocol):
    name: str
    priority: int

    def apply(self, events: list[dict[str, Any]], config: ScoringConfig) -> None:
        ...


def is_vowel(phone: str | None) -> bool:
    return phone in VOWELS


def parse_target_transcription(
    transcription: str,
    phone_inventory: set[str] | None = None,
) -> list[PhoneMetadata]:
    """Tokenize IPA target text and attach stress to the next vowel.

    Syllable separators are ignored because they are not reliable enough for
    scoring. If no explicit stress mark exists, primary stress goes to the
    first vowel.
    """
    inventory = phone_inventory or set(UNIVERSAL_IPA_PHONES)
    vocab = sorted((phone for phone in inventory if phone != "sil"), key=len, reverse=True)

    phones: list[str] = []
    pending_stress: str | None = None
    stress_by_index: dict[int, str] = {}
    index = 0
    source = transcription.strip()
    while index < len(source):
        char = source[index]
        if char in {"/", "[", "]", " ", "\t", "\n", "\r", ".", "·", ":", "ː"}:
            index += 1
            continue
        if char == "ˈ":
            pending_stress = "primary"
            index += 1
            continue
        if char == "ˌ":
            pending_stress = "secondary"
            index += 1
            continue

        phone = next((candidate for candidate in vocab if source.startswith(candidate, index)), None)
        phone_len = len(phone) if phone is not None else 0
        if phone is None and source.startswith("(ə)", index) and "ə" in inventory:
            phone = "ə"
            phone_len = len("(ə)")
        if phone is None and char == "e" and "ɛ" in inventory:
            phone = "ɛ"
            phone_len = len(phone)
        if phone is None:
            raise ValueError(f"Cannot tokenize IPA near {source[index:]!r} in {transcription!r}")
        phones.append(phone)
        if pending_stress and is_vowel(phone):
            stress_by_index[len(phones) - 1] = pending_stress
            pending_stress = None
        index += phone_len

    if phones and not stress_by_index:
        for phone_index, phone in enumerate(phones):
            if is_vowel(phone):
                stress_by_index[phone_index] = "primary"
                break

    metadata = []
    for phone_index, phone in enumerate(phones):
        stress = stress_by_index.get(phone_index)
        if stress is None and is_vowel(phone):
            stress = "unstressed"
        metadata.append(PhoneMetadata(phone=phone, index=phone_index, stress=stress))
    return metadata


def phone_weight(phone: str, metadata: PhoneMetadata | None, config: ScoringConfig) -> float:
    if phone == "sil":
        return 0.0
    if not is_vowel(phone):
        return config.consonant_weight
    if metadata is None:
        return config.vowel_weight_without_stress
    if metadata.stress == "primary":
        return config.stressed_vowel_weight
    if metadata.stress == "secondary":
        return config.secondary_vowel_weight
    if metadata.stress == "unstressed":
        return config.unstressed_vowel_weight
    return config.vowel_weight_without_stress


def _target_event_kind(status: str) -> str:
    if status == "matched":
        return "heard_target"
    if status == "substitution":
        return "heard_substitution"
    if status == "deletion":
        return "missing_target"
    return status


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


class MatchedConfidenceRule:
    name = "matched_confidence"
    priority = 10

    def matches(self, context: EventContext) -> bool:
        return context.status == "matched"

    def apply(self, context: EventContext, config: ScoringConfig) -> RuleDecision:
        prob = float(context.event.get("target_prob", 0.0) or 0.0)
        if prob >= 1.0:
            cost = 0.0
        elif prob >= config.matched_full_credit_prob:
            high_span = 1.0 - config.matched_full_credit_prob
            cost = config.matched_best_possible_cost * (1.0 - prob) / high_span
        elif prob <= config.matched_low_confidence_prob:
            cost = config.matched_max_cost
        else:
            span = config.matched_full_credit_prob - config.matched_low_confidence_prob
            cost = config.matched_best_possible_cost + (
                (config.matched_max_cost - config.matched_best_possible_cost)
                * (config.matched_full_credit_prob - prob)
                / span
            )
        return RuleDecision(
            quality_error=_clamp01(cost),
            rule=self.name,
            message="matched target phone confidence",
        )


class OptionalSchwaSonorantRule:
    name = "optional_schwa_sonorant"
    priority = 20

    PAIRS = {
        ("(ə)l", "l"): 0.0,
        ("l", "(ə)l"): 0.0,
        ("(ə)n", "n"): 0.0,
        ("n", "(ə)n"): 0.0,
    }

    def matches(self, context: EventContext) -> bool:
        return (context.target_phone, context.heard_phone) in self.PAIRS

    def apply(self, context: EventContext, config: ScoringConfig) -> RuleDecision:
        return RuleDecision(
            quality_error=self.PAIRS[(context.target_phone, context.heard_phone)],
            rule=self.name,
            message="optional schwa sonorant realization",
        )


class OptionalSchwaSonorantGroupRule:
    name = "optional_schwa_sonorant_sequence"
    priority = 10

    OPTIONAL_TO_SONORANT = {"(ə)l": "l", "(ə)n": "n"}
    SONORANT_TO_OPTIONAL = {"l": "(ə)l", "n": "(ə)n"}

    def apply(self, events: list[dict[str, Any]], config: ScoringConfig) -> None:
        for index, event in enumerate(events):
            if self._handled(event):
                continue
            target = event.get("target_phone")
            heard = event.get("heard_phone")

            if target in self.OPTIONAL_TO_SONORANT:
                self._accept_optional_target_expansion(events, index, config)
                continue

            if target == "ə":
                self._accept_explicit_sequence_reduction(events, index, config)
                continue

            if target in self.SONORANT_TO_OPTIONAL:
                self._accept_plain_sonorant_optional(events, index, config)

    def _accept_optional_target_expansion(
        self,
        events: list[dict[str, Any]],
        index: int,
        config: ScoringConfig,
    ) -> None:
        event = events[index]
        optional = event["target_phone"]
        sonorant = self.OPTIONAL_TO_SONORANT[optional]
        heard = event.get("heard_phone")
        group_target = f"ə {sonorant}"
        message = f"{optional} realized as ə {sonorant}"

        if event["status"] == "substitution" and heard not in {"ə", sonorant}:
            insertion_index = self._find_nearby_insertion(events, index, sonorant)
            if insertion_index is None:
                return
            group_id = f"{self.name}_{index}_{insertion_index}"
            self._mark_inserted_sonorant_as_optional(
                events[insertion_index],
                event,
                group_id,
                sonorant,
                f"{optional} realized as {sonorant}",
            )
            self._mark_extra_heard(
                event,
                group_id,
                config.default_insertion_cost,
                f"{heard} heard before {optional} realized as {sonorant}",
            )
            return

        if event["status"] == "substitution" and heard in {"ə", sonorant}:
            needed = sonorant if heard == "ə" else "ə"
            insertion_index = self._find_nearby_insertion(events, index, needed)
            if insertion_index is None and heard == sonorant:
                group_id = f"{self.name}_{index}"
                self._mark_accepted(
                    event,
                    group_id,
                    "start",
                    config.optional_schwa_sequence_cost,
                    sonorant,
                    f"{optional} realized as {sonorant}",
                )
                return
            if insertion_index is None:
                return
            group_id = f"{self.name}_{index}_{insertion_index}"
            first_index, second_index = sorted((index, insertion_index))
            self._mark_accepted(
                events[first_index],
                group_id,
                "start",
                config.optional_schwa_sequence_cost,
                group_target,
                message,
            )
            self._mark_accepted(
                events[second_index],
                group_id,
                "continuation",
                0.0,
                group_target,
                message,
            )
            return

        if event["status"] == "deletion":
            schwa_index = self._find_nearby_insertion(events, index, "ə")
            sonorant_index = self._find_nearby_insertion(events, index, sonorant, exclude={schwa_index})
            if schwa_index is None or sonorant_index is None:
                return
            group_id = f"{self.name}_{index}_{schwa_index}_{sonorant_index}"
            event["display_hidden"] = True
            event["wper_cost"] = 0.0
            event["group_id"] = group_id
            event["rule"] = self.name
            for role, event_index, cost in (
                ("start", schwa_index, config.optional_schwa_sequence_cost),
                ("continuation", sonorant_index, 0.0),
            ):
                self._mark_accepted(events[event_index], group_id, role, cost, group_target, message)

    def _accept_explicit_sequence_reduction(
        self,
        events: list[dict[str, Any]],
        index: int,
        config: ScoringConfig,
    ) -> None:
        next_index = self._next_target_event_index(events, index)
        if next_index is None:
            return
        event = events[index]
        next_event = events[next_index]
        sonorant = next_event.get("target_phone")
        optional = self.SONORANT_TO_OPTIONAL.get(sonorant)
        if optional is None:
            return

        group_target = f"ə {sonorant}"
        message = f"ə {sonorant} realized as {optional if self._heard_optional(event, next_event, optional) else sonorant}"

        if event["status"] == "substitution" and event.get("heard_phone") == optional and next_event["status"] == "deletion":
            group_id = f"{self.name}_{index}_{next_index}"
            self._mark_accepted(event, group_id, "start", config.optional_schwa_sequence_cost, group_target, message)
            self._hide_grouped_event(next_event, group_id)
            return

        if (
            event["status"] == "substitution"
            and event.get("heard_phone") == optional
            and next_event["status"] in {"matched", "substitution"}
            and next_event.get("heard_phone") == sonorant
        ):
            group_id = f"{self.name}_{index}_{next_index}"
            self._mark_accepted(event, group_id, "start", config.optional_schwa_sequence_cost, group_target, message)
            self._hide_grouped_event(next_event, group_id)
            return

        if event["status"] == "deletion" and next_event["status"] == "substitution" and next_event.get("heard_phone") == optional:
            group_id = f"{self.name}_{index}_{next_index}"
            self._hide_grouped_event(event, group_id)
            self._mark_accepted(next_event, group_id, "start", config.optional_schwa_sequence_cost, group_target, message)
            return

    def _accept_plain_sonorant_optional(
        self,
        events: list[dict[str, Any]],
        index: int,
        config: ScoringConfig,
    ) -> None:
        event = events[index]
        sonorant = event.get("target_phone")
        optional = self.SONORANT_TO_OPTIONAL[sonorant]
        if event["status"] != "substitution" or event.get("heard_phone") != optional:
            return
        group_id = f"{self.name}_{index}"
        self._mark_accepted(
            event,
            group_id,
            "start",
            config.optional_schwa_sequence_cost,
            sonorant,
            f"{sonorant} realized as {optional}",
        )

    @staticmethod
    def _handled(event: dict[str, Any]) -> bool:
        return bool(event.get("group_id") or event.get("display_hidden"))

    @staticmethod
    def _heard_optional(event: dict[str, Any], next_event: dict[str, Any], optional: str) -> bool:
        return event.get("heard_phone") == optional or next_event.get("heard_phone") == optional

    @staticmethod
    def _next_target_event_index(events: list[dict[str, Any]], index: int) -> int | None:
        target_index = events[index].get("target_index")
        if target_index is None:
            return None
        for candidate_index, event in enumerate(events):
            if event.get("target_index") == target_index + 1:
                return candidate_index
        return None

    @staticmethod
    def _find_nearby_insertion(
        events: list[dict[str, Any]],
        index: int,
        phone: str,
        exclude: set[int | None] | None = None,
    ) -> int | None:
        exclude = exclude or set()
        candidates = []
        event_start = events[index].get("start_frame")
        for candidate_index, event in enumerate(events):
            if candidate_index in exclude or event.get("kind") != "extra_heard":
                continue
            if event.get("heard_phone") != phone or event.get("group_id"):
                continue
            candidate_start = event.get("start_frame")
            distance = abs((candidate_start or 0) - (event_start or 0))
            candidates.append((distance, candidate_index))
        if not candidates:
            return None
        return min(candidates)[1]

    def _mark_accepted(
        self,
        event: dict[str, Any],
        group_id: str,
        group_role: str,
        wper_cost: float,
        group_target: str,
        message: str,
    ) -> None:
        quality_error = 0.0 if wper_cost == 0 else min(0.05, wper_cost)
        event["raw_kind"] = event.get("raw_kind", event["kind"])
        event["kind"] = "accepted_realization"
        event["display_status"] = "accepted"
        event["display_phone"] = event.get("heard_phone")
        event["group_id"] = group_id
        event["group_role"] = group_role
        event["group_target"] = group_target
        event["quality_error"] = round(quality_error, 4)
        event["quality"] = round(1.0 - quality_error, 4)
        event["wper_cost"] = round(wper_cost, 4)
        event["rule"] = self.name
        event["message"] = message

    def _mark_inserted_sonorant_as_optional(
        self,
        event: dict[str, Any],
        target_event: dict[str, Any],
        group_id: str,
        sonorant: str,
        message: str,
    ) -> None:
        event["raw_kind"] = event.get("raw_kind", event["kind"])
        event["raw_status"] = event.get("raw_status", event["status"])
        event["raw_target_phone"] = event.get("raw_target_phone", event.get("target_phone"))
        event["raw_target_index"] = event.get("raw_target_index", event.get("target_index"))
        event["kind"] = "accepted_realization"
        event["display_status"] = "accepted"
        event["display_phone"] = sonorant
        event["target_phone"] = target_event.get("target_phone")
        event["target_index"] = target_event.get("target_index")
        event["group_id"] = group_id
        event["group_role"] = "start"
        event["group_target"] = sonorant
        event["quality_error"] = 0.0
        event["quality"] = 1.0
        event["wper_cost"] = 0.0
        event["rule"] = self.name
        event["message"] = message

    def _mark_extra_heard(
        self,
        event: dict[str, Any],
        group_id: str,
        insertion_cost: float,
        message: str,
    ) -> None:
        event["raw_kind"] = event.get("raw_kind", event["kind"])
        event["raw_status"] = event.get("raw_status", event["status"])
        event["raw_target_phone"] = event.get("raw_target_phone", event.get("target_phone"))
        event["raw_target_index"] = event.get("raw_target_index", event.get("target_index"))
        event["kind"] = "extra_heard"
        event["status"] = "insertion"
        event["display_status"] = "insertion"
        event["display_phone"] = event.get("heard_phone")
        event["target_phone"] = None
        event["target_index"] = None
        event["weight"] = 0.0
        event["group_id"] = group_id
        event["group_role"] = "extra"
        event["quality_error"] = round(insertion_cost, 4)
        event["quality"] = round(1.0 - _clamp01(insertion_cost), 4)
        event["wper_cost"] = round(insertion_cost, 4)
        event["rule"] = self.name
        event["message"] = message

    def _hide_grouped_event(self, event: dict[str, Any], group_id: str) -> None:
        event["display_hidden"] = True
        event["group_id"] = group_id
        event["wper_cost"] = 0.0
        event["rule"] = self.name


class FlapTRule:
    name = "flap_t"
    priority = 30

    def matches(self, context: EventContext) -> bool:
        target = context.target_phone
        heard = context.heard_phone
        if (target, heard) in {("t̬", "t"), ("t", "t̬"), ("t̬", "ɾ")}:
            return True
        if target == "t" and heard == "ɾ":
            return self._valid_flap_context(context)
        return False

    def apply(self, context: EventContext, config: ScoringConfig) -> RuleDecision:
        if (context.target_phone, context.heard_phone) == ("t̬", "t"):
            cost = 0.10
        elif (context.target_phone, context.heard_phone) == ("t", "t̬"):
            cost = 0.15
        else:
            cost = 0.05
        return RuleDecision(
            quality_error=cost,
            rule=self.name,
            message="minor American English flap/allophone difference",
        )

    @staticmethod
    def _valid_flap_context(context: EventContext) -> bool:
        prev_ok = is_vowel(context.prev_target_phone) or context.prev_target_phone == "r"
        next_ok = is_vowel(context.next_target_phone) or context.next_target_phone in {"l", "(ə)l"}
        stress_ok = context.next_vowel_stress in {None, "unstressed"}
        return prev_ok and next_ok and stress_ok


class SimilarVowelRule:
    name = "similar_vowel"
    priority = 40

    COSTS = {
        ("ɛ", "æ"): 0.40,
        ("æ", "ɛ"): 0.40,
        ("ɪ", "i"): 0.35,
        ("i", "ɪ"): 0.35,
        ("ʊ", "u"): 0.50,
        ("u", "ʊ"): 0.50,
        ("ə", "ʌ"): 0.25,
        ("ʌ", "ə"): 0.25,
        ("ɚ", "ɝ"): 0.40,
        ("ɝ", "ɚ"): 0.40,
        ("ɑ", "ɔ"): 0.10,
        ("ɔ", "ɑ"): 0.10,
        ("ɑ", "oʊ"): 0.55,
        ("oʊ", "ɑ"): 0.55,
        ("ɔ", "oʊ"): 0.45,
        ("oʊ", "ɔ"): 0.45,
        ("ʌ", "ɑ"): 0.3,
        ("ɑ", "ʌ"): 0.3,
        ("ɪ", "ə"): 0.4,
        ("ə", "ɪ"): 0.4,        
        #ɪ ->ɛ
    }

    def matches(self, context: EventContext) -> bool:
        return (context.target_phone, context.heard_phone) in self.COSTS

    def apply(self, context: EventContext, config: ScoringConfig) -> RuleDecision:
        return RuleDecision(
            quality_error=self.COSTS[(context.target_phone, context.heard_phone)],
            rule=self.name,
            message="similar vowel substitution",
        )


class StopVoicingRule:
    name = "stop_voicing"
    priority = 50

    PAIRS = {
        ("p", "b"),
        ("b", "p"),
        ("t", "d"),
        ("d", "t"),
        ("k", "ɡ"),
        ("ɡ", "k"),
    }

    def matches(self, context: EventContext) -> bool:
        return (context.target_phone, context.heard_phone) in self.PAIRS

    def apply(self, context: EventContext, config: ScoringConfig) -> RuleDecision:
        return RuleDecision(
            quality_error=0.50,
            rule=self.name,
            message="same stop with different voicing",
        )


class UnstressedVowelSubstitutionRule:
    name = "unstressed_vowel_substitution"
    priority = 60

    def matches(self, context: EventContext) -> bool:
        return (
            context.status == "substitution"
            and context.metadata is not None
            and context.metadata.stress == "unstressed"
            and is_vowel(context.target_phone)
            and is_vowel(context.heard_phone)
        )

    def apply(self, context: EventContext, config: ScoringConfig) -> RuleDecision:
        return RuleDecision(
            quality_error=config.unstressed_vowel_substitution_cost,
            rule=self.name,
            message="unstressed vowel replaced by another vowel",
        )


class DefaultSubstitutionRule:
    name = "default_substitution"
    priority = 90

    def matches(self, context: EventContext) -> bool:
        return context.status == "substitution"

    def apply(self, context: EventContext, config: ScoringConfig) -> RuleDecision:
        return RuleDecision(
            quality_error=config.default_substitution_cost,
            rule=self.name,
            message="phone substitution",
        )


class DefaultDeletionRule:
    name = "default_deletion"
    priority = 100

    def matches(self, context: EventContext) -> bool:
        return context.status == "deletion"

    def apply(self, context: EventContext, config: ScoringConfig) -> RuleDecision:
        return RuleDecision(
            quality_error=config.default_deletion_cost,
            rule=self.name,
            message="missing target phone",
        )


class DefaultInsertionRule:
    name = "default_insertion"
    priority = 110

    def matches(self, context: EventContext) -> bool:
        return context.status == "insertion"

    def apply(self, context: EventContext, config: ScoringConfig) -> RuleDecision:
        return RuleDecision(
            quality_error=config.default_insertion_cost,
            rule=self.name,
            message="extra heard phone",
        )


DEFAULT_RULES: tuple[ScoringRule, ...] = (
    MatchedConfidenceRule(),
    OptionalSchwaSonorantRule(),
    FlapTRule(),
    SimilarVowelRule(),
    StopVoicingRule(),
    UnstressedVowelSubstitutionRule(),
    DefaultSubstitutionRule(),
    DefaultDeletionRule(),
    DefaultInsertionRule(),
)

DEFAULT_TIMELINE_RULES: tuple[TimelineRule, ...] = (
    OptionalSchwaSonorantGroupRule(),
)


class PronunciationScorer:
    def __init__(
        self,
        rules: list[ScoringRule] | None = None,
        timeline_rules: list[TimelineRule] | None = None,
        config: ScoringConfig | None = None,
    ) -> None:
        self.config = config or ScoringConfig()
        self.rules = sorted(rules or list(DEFAULT_RULES), key=lambda rule: rule.priority)
        self.timeline_rules = sorted(
            timeline_rules or list(DEFAULT_TIMELINE_RULES),
            key=lambda rule: rule.priority,
        )

    @classmethod
    def default(cls) -> "PronunciationScorer":
        return cls()

    def score(
        self,
        alignment: dict[str, Any],
        target_transcription: str | None = None,
        target_metadata: list[PhoneMetadata] | None = None,
    ) -> dict[str, Any]:
        target_phones = [row["phone"] for row in alignment.get("phones", [])]
        if target_metadata is None:
            if target_transcription is not None:
                target_metadata = parse_target_transcription(target_transcription, set(target_phones))
            else:
                target_metadata = [
                    PhoneMetadata(phone=row["phone"], index=index)
                    for index, row in enumerate(alignment.get("phones", []))
                ]

        target_metadata_by_index = {item.index: item for item in target_metadata}
        diagnostic_events = self._build_events(alignment, target_metadata_by_index, target_phones)
        events = self._build_display_events(diagnostic_events)
        error_cost = round(sum(float(event["wper_cost"]) for event in events), 4)
        total_target_weight = round(
            sum(
                phone_weight(phone, target_metadata_by_index.get(index), self.config)
                for index, phone in enumerate(target_phones)
            ),
            4,
        )
        wper = round(error_cost / max(total_target_weight, 1.0e-8), 4)
        return {
            "wper": wper,
            "weighted_error_cost": error_cost,
            "total_target_weight": total_target_weight,
            "events": events,
            "diagnostic_events": diagnostic_events,
            "summary": self._summary(events),
        }

    def _build_display_events(self, diagnostic_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        events = deepcopy(diagnostic_events)
        for rule in self.timeline_rules:
            rule.apply(events, self.config)
        return [event for event in events if not event.get("display_hidden")]

    def _build_events(
        self,
        alignment: dict[str, Any],
        target_metadata_by_index: dict[int, PhoneMetadata],
        target_phones: list[str],
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for index, row in enumerate(alignment.get("phones", [])):
            context = self._target_context(row, index, target_metadata_by_index, target_phones)
            rows.append(self._score_context(context))

        for insertion_index, row in enumerate(alignment.get("insertions", [])):
            context = self._insertion_context(row, insertion_index, target_phones, alignment)
            rows.append(self._score_context(context))

        return sorted(
            rows,
            key=lambda event: (
                event["start_frame"] is None,
                event["start_frame"] if event["start_frame"] is not None else 0,
                event.get("target_index") is None,
                event.get("target_index") if event.get("target_index") is not None else 10**9,
            ),
        )

    def _target_context(
        self,
        row: dict[str, Any],
        index: int,
        target_metadata_by_index: dict[int, PhoneMetadata],
        target_phones: list[str],
    ) -> EventContext:
        status = row["status"]
        target_phone = row["phone"]
        heard_phone = target_phone if status == "matched" else row.get("best_phone")
        if status == "deletion" or heard_phone == "<blank>":
            heard_phone = None
        return EventContext(
            event=row,
            target_index=index,
            target_phone=target_phone,
            heard_phone=heard_phone,
            status=status,
            metadata=target_metadata_by_index.get(index),
            prev_target_phone=target_phones[index - 1] if index > 0 else None,
            next_target_phone=target_phones[index + 1] if index + 1 < len(target_phones) else None,
            next_vowel_stress=self._next_vowel_stress(index, target_metadata_by_index, target_phones),
        )

    def _insertion_context(
        self,
        row: dict[str, Any],
        insertion_index: int,
        target_phones: list[str],
        alignment: dict[str, Any],
    ) -> EventContext:
        prev_index = None
        next_index = None
        start_frame = row.get("start_frame")
        for index, target_row in enumerate(alignment.get("phones", [])):
            target_start = target_row.get("start_frame")
            if start_frame is None or target_start is None:
                continue
            if target_start <= start_frame:
                prev_index = index
            elif next_index is None:
                next_index = index
        return EventContext(
            event=row | {"insertion_index": insertion_index},
            target_index=None,
            target_phone=None,
            heard_phone=row["phone"],
            status="insertion",
            metadata=None,
            prev_target_phone=target_phones[prev_index] if prev_index is not None else None,
            next_target_phone=target_phones[next_index] if next_index is not None else None,
            next_vowel_stress=None,
        )

    def _next_vowel_stress(
        self,
        index: int,
        target_metadata_by_index: dict[int, PhoneMetadata],
        target_phones: list[str],
    ) -> str | None:
        for next_index in range(index + 1, len(target_phones)):
            if is_vowel(target_phones[next_index]):
                metadata = target_metadata_by_index.get(next_index)
                return metadata.stress if metadata is not None else None
        return None

    def _score_context(self, context: EventContext) -> dict[str, Any]:
        decision = self._apply_rules(context)
        weight = (
            phone_weight(context.target_phone, context.metadata, self.config)
            if context.target_phone is not None
            else 0.0
        )
        if context.status == "insertion":
            wper_cost = decision.quality_error
        else:
            wper_cost = weight * decision.quality_error
        return {
            "kind": "extra_heard" if context.status == "insertion" else _target_event_kind(context.status),
            "status": context.status,
            "target_index": context.target_index,
            "target_phone": context.target_phone,
            "heard_phone": context.heard_phone,
            "start_frame": context.event.get("start_frame"),
            "end_frame": context.event.get("end_frame"),
            "frames": context.event.get("frames"),
            "target_prob": context.event.get("target_prob"),
            "best_phone": context.event.get("best_phone"),
            "best_prob": context.event.get("best_prob", context.event.get("prob")),
            "stress": context.metadata.stress if context.metadata is not None else None,
            "weight": round(weight, 4),
            "quality_error": round(decision.quality_error, 4),
            "quality": round(1.0 - _clamp01(decision.quality_error), 4),
            "wper_cost": round(wper_cost, 4),
            "rule": decision.rule,
            "message": decision.message,
        }

    def _apply_rules(self, context: EventContext) -> RuleDecision:
        for rule in self.rules:
            if rule.matches(context):
                return rule.apply(context, self.config)
        return RuleDecision(
            quality_error=1.0,
            rule="unhandled_event",
            message="unhandled pronunciation event",
        )

    @staticmethod
    def _summary(events: list[dict[str, Any]]) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for event in events:
            status = event["status"]
            counts[status] = counts.get(status, 0) + 1
        return {
            "counts": counts,
            "insertions": counts.get("insertion", 0),
            "deletions": counts.get("deletion", 0),
            "substitutions": counts.get("substitution", 0),
        }


def score_pronunciation_alignment(
    alignment: dict[str, Any],
    target_transcription: str | None = None,
    target_metadata: list[PhoneMetadata] | None = None,
    config: ScoringConfig | None = None,
    rules: list[ScoringRule] | None = None,
    timeline_rules: list[TimelineRule] | None = None,
) -> dict[str, Any]:
    scorer = PronunciationScorer(rules=rules, timeline_rules=timeline_rules, config=config)
    return scorer.score(
        alignment,
        target_transcription=target_transcription,
        target_metadata=target_metadata,
    )
