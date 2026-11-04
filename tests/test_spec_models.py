"""Unit tests for the voice spec models. Local files only, no network calls."""

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from campaign_agent.spec.models import (
    Example,
    GlossaryEntry,
    LengthLimit,
    PersonalityPair,
    Vocabulary,
    VoiceSpec,
)

SPEC_PATH = Path(__file__).parents[1] / "data/brands/brand_a/voice_spec.yaml"


@pytest.fixture
def raw_spec() -> dict:
    """The real spec as a plain dict. Each test gets a fresh copy, so it can change it."""
    return yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))


def invalid(raw: dict) -> list[dict]:
    """Validate `raw` as a VoiceSpec, expect it to fail, and return Pydantic's errors."""
    with pytest.raises(ValidationError) as exc:
        VoiceSpec.model_validate(raw)
    return exc.value.errors()


def single_error(raw: dict) -> dict:
    """Expect exactly one error, so a test can't pass because something else is broken."""
    errors = invalid(raw)
    assert len(errors) == 1, errors
    return errors[0]


# --- Small models ----------------------------------------------------------------------


def test_length_limit_accepts_min_below_max():
    limit = LengthLimit(min=40, max=150)
    assert (limit.min, limit.max) == (40, 150)


@pytest.mark.parametrize(
    ("low", "high"),
    [
        (150, 40),  # min above max
        (40, 40),  # min equal to max
        (0, 40),  # min below 1
    ],
)
def test_length_limit_rejects_bad_limits(low, high):
    with pytest.raises(ValidationError):
        LengthLimit(min=low, max=high)


def test_personality_pair_reads_yaml_keys():
    pair = PersonalityPair.model_validate({"is": "warm", "not": "gushing"})
    assert (pair.is_, pair.not_) == ("warm", "gushing")


def test_personality_pair_accepts_python_names():
    pair = PersonalityPair(is_="warm", not_="gushing")
    assert pair.is_ == "warm"


def test_personality_pair_rejects_same_trait_twice():
    with pytest.raises(ValidationError, match="the same"):
        PersonalityPair.model_validate({"is": "Warm", "not": "warm"})


def test_glossary_term_cannot_be_its_own_wrong_form():
    with pytest.raises(ValidationError, match="wrong form of itself"):
        GlossaryEntry(term="e-bike", wrong=["ebike", "e-bike"])


@pytest.mark.parametrize("banned", [["slay", "slay"], ["slay", "SLAY"]])
def test_vocabulary_rejects_duplicate_banned_words(banned):
    with pytest.raises(ValidationError, match="duplicate banned words"):
        Vocabulary(banned=banned)


def test_vocabulary_rejects_duplicate_glossary_terms():
    entry = {"term": "e-bike", "wrong": ["ebike"]}
    with pytest.raises(ValidationError, match="duplicate glossary terms"):
        Vocabulary.model_validate({"banned": ["slay"], "glossary": [entry, entry]})


def test_example_texts_must_differ():
    with pytest.raises(ValidationError, match="the same text"):
        Example(off_brand="Hello.", on_brand="Hello.")


# --- The whole spec: passing case ------------------------------------------------------


def test_real_spec_loads(raw_spec):
    spec = VoiceSpec.model_validate(raw_spec)
    assert spec.name == "Moien Vëlo"
    assert spec.version == "1.0.0"
    assert spec.voice.personality[0].is_ == "reassuring"
    assert spec.tone_by_channel.web.enthusiastic_matter_of_fact == 0.8
    assert spec.style.length_words.social.max == 150
    assert spec.style.emoji_max.web == 0
    assert "eco-friendly" in spec.vocabulary.banned


def test_spec_is_frozen(raw_spec):
    spec = VoiceSpec.model_validate(raw_spec)
    with pytest.raises(ValidationError):
        spec.name = "Another Brand"


# --- The whole spec: failing cases -----------------------------------------------------
# Each test breaks one thing in the real spec, then checks that Pydantic rejects it with
# exactly one error, at the right place (`loc` is the path to the bad field).


def test_unknown_top_level_key_is_rejected(raw_spec):
    raw_spec["emoji_maxx"] = 1
    error = single_error(raw_spec)
    assert error["type"] == "extra_forbidden"
    assert error["loc"] == ("emoji_maxx",)


def test_unknown_nested_key_is_rejected(raw_spec):
    raw_spec["style"]["emoji_maxx"] = {"social": 1, "email": 0, "web": 0}
    error = single_error(raw_spec)
    assert error["type"] == "extra_forbidden"
    assert error["loc"] == ("style", "emoji_maxx")


@pytest.mark.parametrize("score", [1.5, -0.1])
def test_tone_score_outside_0_to_1_is_rejected(raw_spec, score):
    raw_spec["tone_by_channel"]["social"]["funny_serious"] = score
    error = single_error(raw_spec)
    assert error["loc"] == ("tone_by_channel", "social", "funny_serious")


def test_missing_channel_is_rejected(raw_spec):
    del raw_spec["style"]["emoji_max"]["web"]
    error = single_error(raw_spec)
    assert error["type"] == "missing"
    assert error["loc"] == ("style", "emoji_max", "web")


def test_unknown_contractions_value_is_rejected(raw_spec):
    raw_spec["style"]["contractions"] = "sometimes"
    error = single_error(raw_spec)
    assert error["type"] == "literal_error"
    assert error["loc"] == ("style", "contractions")


def test_negative_limit_is_rejected(raw_spec):
    raw_spec["style"]["emoji_max"]["social"] = -1
    error = single_error(raw_spec)
    assert error["loc"] == ("style", "emoji_max", "social")


def test_length_min_above_max_is_rejected(raw_spec):
    raw_spec["style"]["length_words"]["web"] = {"min": 200, "max": 30}
    error = single_error(raw_spec)
    assert error["loc"] == ("style", "length_words", "web")
    assert "must be less than max" in error["msg"]


def test_empty_personality_is_rejected(raw_spec):
    raw_spec["voice"]["personality"] = []
    error = single_error(raw_spec)
    assert error["loc"] == ("voice", "personality")


def test_number_as_string_is_rejected(raw_spec):
    # strict=True: "8" is a string, not the number 8, even though it looks like one.
    raw_spec["style"]["reading_grade_max"] = "8"
    error = single_error(raw_spec)
    assert error["loc"] == ("style", "reading_grade_max")


@pytest.mark.parametrize("version", ["1.0", "v1.0.0", "1.0.0-beta"])
def test_bad_version_is_rejected(raw_spec, version):
    raw_spec["version"] = version
    error = single_error(raw_spec)
    assert error["loc"] == ("version",)


@pytest.mark.parametrize("spelling", ["english", "en-gb", "EN-GB"])
def test_bad_spelling_code_is_rejected(raw_spec, spelling):
    raw_spec["style"]["spelling"] = spelling
    error = single_error(raw_spec)
    assert error["loc"] == ("style", "spelling")
