"""Unit tests for the deterministic rule checks. Local files only, no network calls."""

import json

import pytest

from campaign_agent.spec import rules
from campaign_agent.spec.loader import DATA_DIR, load_spec

CORPUS_PATH = DATA_DIR / "brands/brand_a/corpus.jsonl"
CORPUS = [
    json.loads(line)
    for line in CORPUS_PATH.read_text(encoding="utf-8").splitlines()
    if line.strip()
]

# A clean social post: right length, no banned words, simple sentences.
CLEAN_SOCIAL = (
    "Our Stroller helps you along up to 15 km/h, then lets you set the pace. "
    "The frame is low, so you step through rather than swing a leg over. "
    "The brakes need only a light touch. Come and try one at the showroom in Bertrange. "
    "We'll put the kettle on."
)


@pytest.fixture(scope="module")
def spec():
    # scope="module": load once for this file. Safe because the spec is frozen.
    return load_spec()


def rule_names(violations):
    return [v.rule for v in violations]


def test_clean_text_passes_every_rule(spec):
    assert rules.check_all(CLEAN_SOCIAL, "social", spec) == []


# --- Banned words ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "Our eco-friendly bikes.",
        "Our Eco-Friendly bikes.",  # case doesn't matter
        "This bike, no cap, is great.",  # multi-word phrase
        "It’s giving comfort.",  # curly apostrophe is normalised first
        "Perfect for the elderly.",
    ],
)
def test_banned_words_are_flagged(spec, text):
    violations = rules.check_banned_words(text, "social", spec)
    assert rule_names(violations) == ["banned_word"]
    assert violations[0].found is not None


@pytest.mark.parametrize(
    "text",
    [
        "Check the suspension.",  # "sus" inside a longer word
        "We're based in Bertrange.",  # ordinary words that slang also uses aren't banned
        "A revolution in comfort.",  # "revolutionary" is banned, "revolution" isn't
    ],
)
def test_banned_words_need_a_whole_word_match(spec, text):
    assert rules.check_banned_words(text, "social", spec) == []


def test_every_banned_word_is_reported(spec):
    violations = rules.check_banned_words("A revolutionary, eco-friendly ride.", "social", spec)
    assert sorted(v.found.lower() for v in violations) == ["eco-friendly", "revolutionary"]


# --- Glossary --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "wrong"),
    [
        ("Try the Cafe Racer.", "Cafe Racer"),
        ("Moien Velo makes slow bikes.", "Moien Velo"),
        ("Our ebike range.", "ebike"),
        ("Up to 15 kph.", "kph"),
        ("Use gentle effort mode on hills.", "gentle effort mode"),
    ],
)
def test_wrong_glossary_forms_are_flagged(spec, text, wrong):
    violations = rules.check_glossary(text, "social", spec)
    assert [v.found for v in violations] == [wrong]


def test_correct_glossary_forms_pass(spec):
    text = "Moien Vëlo's Café Racer is an e-bike that helps up to 10 km/h in Gentle Effort mode."
    assert rules.check_glossary(text, "social", spec) == []


def test_glossary_is_case_sensitive(spec):
    # "E-bike" at the start of a sentence is fine; only "E-Bike" is listed as wrong.
    assert rules.check_glossary("E-bike riders welcome.", "social", spec) == []
    assert rule_names(rules.check_glossary("E-Bike riders welcome.", "social", spec)) == [
        "glossary"
    ]


# --- Apostrophes -----------------------------------------------------------------------


def test_curly_apostrophe_is_flagged(spec):
    assert rule_names(rules.check_apostrophes("We’re open.", "social", spec)) == ["apostrophe"]


def test_straight_apostrophe_passes(spec):
    assert rules.check_apostrophes("We're open.", "social", spec) == []


# --- Length ----------------------------------------------------------------------------


def words(n: int) -> str:
    return " ".join(["ride"] * n)


@pytest.mark.parametrize(
    ("channel", "n", "ok"),
    [
        ("social", 40, True),  # exactly the minimum
        ("social", 39, False),
        ("social", 150, True),  # exactly the maximum
        ("social", 151, False),
        ("web", 30, True),
        ("web", 121, False),
        ("email", 59, False),
    ],
)
def test_length_limits_per_channel(spec, channel, n, ok):
    violations = rules.check_length(words(n), channel, spec)
    assert (violations == []) is ok


def test_length_message_says_what_to_do(spec):
    [violation] = rules.check_length(words(10), "social", spec)
    assert "Too short: 10 words" in violation.message
    assert "at least 40" in violation.message


# --- Emoji, exclamation marks, hashtags ------------------------------------------------


@pytest.mark.parametrize(
    ("text", "channel", "ok"),
    [
        ("Coffee time ☕", "social", True),  # social allows 1
        ("Coffee time ☕🍰", "social", False),
        ("Coffee time ☕", "web", False),  # web allows none
        ("Coffee time", "email", True),
    ],
)
def test_emoji_limits(spec, text, channel, ok):
    assert (rules.check_emoji(text, channel, spec) == []) is ok


@pytest.mark.parametrize(
    ("text", "channel", "ok"),
    [
        ("Come and ride!", "social", True),
        ("Come! Ride!", "social", False),
        ("Come and ride!", "web", False),
    ],
)
def test_exclamation_limits(spec, text, channel, ok):
    assert (rules.check_exclamations(text, channel, spec) == []) is ok


@pytest.mark.parametrize(
    ("text", "channel", "ok"),
    [
        ("Slow rides. #Luxembourg #Cycling #Moselle", "social", True),
        ("Slow rides. #Luxembourg #Cycling #Moselle #Bikes", "social", False),
        ("Slow rides. #Luxembourg", "web", False),
        ("Item #3 on the list", "web", False),  # counted: '#3' looks like a hashtag
        ("Number 3 on the list", "web", True),
    ],
)
def test_hashtag_limits(spec, text, channel, ok):
    assert (rules.check_hashtags(text, channel, spec) == []) is ok


def test_count_message_names_the_limit(spec):
    [violation] = rules.check_emoji("Hello ☕", "web", spec)
    assert "none are allowed" in violation.message
    assert violation.found == "☕"


# --- Reading grade ---------------------------------------------------------------------


def test_simple_text_passes_reading_grade(spec):
    assert rules.check_reading_grade(CLEAN_SOCIAL, "social", spec) == []


def test_complex_text_fails_reading_grade(spec):
    text = (
        "Notwithstanding considerable organisational, infrastructural and environmental "
        "complexities, our comprehensively engineered electrically assisted bicycles "
        "systematically demonstrate extraordinary operational reliability."
    )
    assert rule_names(rules.check_reading_grade(text, "web", spec)) == ["reading_grade"]


# --- All rules together ----------------------------------------------------------------


def test_check_all_reports_every_broken_rule(spec):
    text = "Our revolutionary Cafe Racer! Amazing! ☕🍰"
    found = set(rule_names(rules.check_all(text, "web", spec)))
    # "revolutionary" alone pushes the Flesch-Kincaid grade of a 7-word text over 8.
    assert found == {"banned_word", "glossary", "length", "emoji", "exclamation", "reading_grade"}


def test_off_brand_examples_in_the_spec_break_a_rule(spec):
    # The spec's own off-brand examples should be caught, as far as rules can catch them.
    caught = [
        ex.off_brand
        for ex in spec.examples
        if rules.check_banned_words(ex.off_brand, "social", spec)
        or rules.check_exclamations(ex.off_brand, "web", spec)
    ]
    assert len(caught) == len(spec.examples)


@pytest.mark.parametrize("item", CORPUS, ids=[item["id"] for item in CORPUS])
def test_approved_corpus_passes_every_rule(spec, item):
    # The corpus is the brand's approved writing, so it must pass the brand's own rules.
    # If this fails, either a text or a rule has drifted.
    assert rules.check_all(item["text"], item["channel"], spec) == []
