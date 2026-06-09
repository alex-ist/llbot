import re

try:
    import nltk
    from nltk.corpus import cmudict
except ModuleNotFoundError:
    nltk = None
    cmudict = None


_ARPA2IPA = {
    "B": "b",
    "D": "d",
    "G": "ɡ",
    "P": "p",
    "T": "t",
    "K": "k",
    "CH": "tʃ",
    "JH": "dʒ",
    "F": "f",
    "V": "v",
    "TH": "θ",
    "DH": "ð",
    "S": "s",
    "Z": "z",
    "SH": "ʃ",
    "ZH": "ʒ",
    "HH": "h",
    "M": "m",
    "N": "n",
    "NG": "ŋ",
    "L": "l",
    "R": "r",
    "W": "w",
    "Y": "j",
    "IY": "i",
    "IH": "ɪ",
    "EH": "ɛ",
    "EY": "eɪ",
    "AE": "æ",
    "AA": "ɑ",
    "AW": "aʊ",
    "AY": "aɪ",
    "AH": "ə",
    "AO": "ɔ",
    "OY": "ɔɪ",
    "OW": "oʊ",
    "UH": "ʊ",
    "UW": "u",
    "ER": "ɚ",
}

_STRESSABLE_ARPA = {
    "IY",
    "IH",
    "EH",
    "EY",
    "AE",
    "AA",
    "AW",
    "AY",
    "AH",
    "AO",
    "OY",
    "OW",
    "UH",
    "UW",
    "ER",
}

_CMU = None


def _cmu_dict():
    global _CMU
    if nltk is None or cmudict is None:
        return None
    if _CMU is None:
        try:
            _CMU = cmudict.dict()
        except LookupError:
            nltk.download("cmudict", quiet=True)
            try:
                _CMU = cmudict.dict()
            except LookupError:
                return None
    return _CMU


def _ipa_for_arpa_phone(key: str, stress: str | None) -> str:
    if key == "AH" and stress in {"1", "2"}:
        return "ʌ"
    if key == "ER" and stress in {"1", "2"}:
        return "ɝ"
    return _ARPA2IPA.get(key, key.lower())


def arpa_phones_to_ipa(phones: list[str]) -> str:
    out = []
    for phone in phones:
        match = re.match(r"^([A-Z]+)(\d)?$", phone.upper())
        key = match.group(1) if match else re.sub(r"\d+$", "", phone).upper()
        stress = match.group(2) if match else None
        ipa = _ipa_for_arpa_phone(key, stress)

        if key in _STRESSABLE_ARPA:
            if stress == "1":
                ipa = "ˈ" + ipa
            elif stress == "2":
                ipa = "ˌ" + ipa

        out.append(ipa)
    return "".join(out)


def _phrase_text(text: str) -> str:
    return re.sub(r"\([^)]*\)", " ", text)


def _expression_tokens(text: str) -> list[str]:
    return [
        token.lower()
        for token in re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", _phrase_text(text))
    ]


def is_multiword_expression(text: str) -> bool:
    phrase = _phrase_text(text).strip()
    return bool(re.search(r"\s", phrase)) and len(_expression_tokens(phrase)) > 1


def text_ipa(text: str) -> str | None:
    phrase = _phrase_text(text).strip()
    tokens = _expression_tokens(phrase)
    if not tokens:
        return None

    cmu = _cmu_dict()
    if cmu is None:
        return None

    parts = []
    for token in tokens:
        pronunciations = cmu.get(token)
        if not pronunciations:
            return None
        parts.append(arpa_phones_to_ipa(pronunciations[0]))
    return " ".join(parts) or None


def expression_ipa(text: str) -> str | None:
    phrase = _phrase_text(text).strip()
    if not re.search(r"\s", phrase) or len(_expression_tokens(phrase)) <= 1:
        return None
    return text_ipa(text)
