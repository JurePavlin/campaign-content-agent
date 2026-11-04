"""Deterministic rule checks: hard brand rules enforced in code, not only in the prompt.

Every check has the same shape, `(text, channel, spec) -> list[Violation]`, so the
`check_rules` node can run them all in a loop. Each violation's message is written for the
writer model: it says what to change and why, so the next draft can fix it.
"""

import re
from collections.abc import Callable
from typing import Literal

import textstat
from pydantic import BaseModel, ConfigDict

from campaign_agent.spec.models import Channel, VoiceSpec

Rule = Literal[
    "banned_word",
    "glossary",
    "apostrophe",
    "length",
    "emoji",
    "exclamation",
    "hashtags",
    "reading_grade",
]


class Violation(BaseModel):
    model_config = ConfigDict(frozen=True)

    rule: Rule
    message: str  # instruction for the writer: what to change, and why
    found: str | None = None  # the exact text that broke the rule, if there is one


Check = Callable[[str, Channel, VoiceSpec], list[Violation]]

CURLY_QUOTES = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'})
# The main emoji blocks. Not exhaustive (Unicode has no simple "is emoji" test), but it
# covers the pictographs, symbols and dingbats a writer model actually produces.
EMOJI = re.compile("[\U0001f300-\U0001faff☀-➿]")
HASHTAG = re.compile(r"(?<!\w)#\w+")


def normalise(text: str) -> str:
    """Curly quotes to straight ones, so "it’s giving" can't slip past "it's giving"."""
    return text.translate(CURLY_QUOTES)


def phrase_pattern(phrase: str, *, ignore_case: bool) -> re.Pattern[str]:
    """Match `phrase` as a whole word or phrase: "sus" must not match "suspension".

    Hyphens count as part of a word, so "e-bike" isn't matched inside "e-bikes-only".
    Inflected forms ("slayed") aren't matched either; list them in the spec if needed.
    """
    flags = re.IGNORECASE if ignore_case else 0
    return re.compile(rf"(?<![\w-]){re.escape(phrase)}(?![\w-])", flags)


def check_banned_words(text: str, channel: Channel, spec: VoiceSpec) -> list[Violation]:
    """Banned words and phrases, matched case-insensitively."""
    text = normalise(text)
    violations = []
    for word in spec.vocabulary.banned:
        if match := phrase_pattern(word, ignore_case=True).search(text):
            violations.append(
                Violation(
                    rule="banned_word",
                    message=f"Remove {match.group()!r}: it's on the brand's banned list.",
                    found=match.group(),
                )
            )
    return violations


def check_glossary(text: str, channel: Channel, spec: VoiceSpec) -> list[Violation]:
    """Wrong forms of glossary terms, matched case-sensitively ("Cafe Racer" vs "Café Racer")."""
    text = normalise(text)
    violations = []
    for entry in spec.vocabulary.glossary:
        for wrong in entry.wrong:
            if phrase_pattern(wrong, ignore_case=False).search(text):
                violations.append(
                    Violation(
                        rule="glossary",
                        message=f"Write {entry.term!r}, not {wrong!r}.",
                        found=wrong,
                    )
                )
    return violations


def check_apostrophes(text: str, channel: Channel, spec: VoiceSpec) -> list[Violation]:
    if spec.style.apostrophe == "straight" and ("’" in text or "‘" in text):
        return [
            Violation(
                rule="apostrophe",
                message="Use straight apostrophes and quotes (') instead of curly ones (’).",
                found="’" if "’" in text else "‘",
            )
        ]
    return []


def check_length(text: str, channel: Channel, spec: VoiceSpec) -> list[Violation]:
    """Word count, splitting on whitespace. Hashtags count as words."""
    limit = getattr(spec.style.length_words, channel)
    words = len(text.split())
    if words < limit.min:
        return [
            Violation(
                rule="length",
                message=f"Too short: {words} words. A {channel} piece needs at least {limit.min}.",
            )
        ]
    if words > limit.max:
        return [
            Violation(
                rule="length",
                message=f"Too long: {words} words. A {channel} piece allows at most {limit.max}.",
            )
        ]
    return []


def _count_limit(
    rule: Rule, label: str, found: list[str], channel: Channel, maximum: int
) -> list[Violation]:
    """Shared logic for the 'at most N of something per channel' rules."""
    if len(found) <= maximum:
        return []
    allowed = "none are allowed" if maximum == 0 else f"at most {maximum} allowed"
    return [
        Violation(
            rule=rule,
            message=f"Too many {label}: {len(found)} found, {allowed} in a {channel} piece.",
            found=" ".join(found),
        )
    ]


def check_emoji(text: str, channel: Channel, spec: VoiceSpec) -> list[Violation]:
    found = EMOJI.findall(text)
    return _count_limit("emoji", "emoji", found, channel, getattr(spec.style.emoji_max, channel))


def check_exclamations(text: str, channel: Channel, spec: VoiceSpec) -> list[Violation]:
    found = ["!"] * text.count("!")
    maximum = getattr(spec.style.exclamation_max, channel)
    return _count_limit("exclamation", "exclamation marks", found, channel, maximum)


def check_hashtags(text: str, channel: Channel, spec: VoiceSpec) -> list[Violation]:
    found = HASHTAG.findall(text)
    maximum = getattr(spec.style.hashtags_max, channel)
    return _count_limit("hashtags", "hashtags", found, channel, maximum)


def check_reading_grade(text: str, channel: Channel, spec: VoiceSpec) -> list[Violation]:
    """Flesch-Kincaid grade. Based on sentence and word length, so it's noisy on very short
    texts and can be gamed with choppy sentences; the critic judges readability as well."""
    grade = textstat.flesch_kincaid_grade(text)
    maximum = spec.style.reading_grade_max
    if grade > maximum:
        return [
            Violation(
                rule="reading_grade",
                message=(
                    f"Reading grade is {grade:.1f}; the maximum is {maximum:g}. "
                    "Use shorter sentences and simpler words."
                ),
            )
        ]
    return []


CHECKS: tuple[Check, ...] = (
    check_banned_words,
    check_glossary,
    check_apostrophes,
    check_length,
    check_emoji,
    check_exclamations,
    check_hashtags,
    check_reading_grade,
)


def check_all(text: str, channel: Channel, spec: VoiceSpec) -> list[Violation]:
    """Run every rule. An empty list means the text passes all hard rules."""
    return [violation for check in CHECKS for violation in check(text, channel, spec)]
