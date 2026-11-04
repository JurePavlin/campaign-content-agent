"""Pydantic models for a brand's voice spec (data/brands/<brand>/voice_spec.yaml).

Loading the YAML into these models checks every field, so a malformed spec fails at
load time with a clear error instead of halfway through an agent run.
"""

from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

Channel = Literal["social", "email", "web"]

# Reusable field types: the constraint is written once and shared by every field using it.
NonEmptyStr = Annotated[str, Field(min_length=1)]
Score = Annotated[float, Field(ge=0, le=1)]  # one tone dimension, 0 to 1
NonNegativeInt = Annotated[int, Field(ge=0)]  # a "max" count; 0 means "none allowed"


class StrictModel(BaseModel):
    """Base for every spec model.

    extra="forbid": an unknown key (a typo such as `emoji_maxx`) is an error, not ignored.
    frozen=True: a loaded spec can't be changed by accident while the agent runs.
    strict=True: no silent type conversion, so `"8"` (a string) isn't accepted as the
    number 8. YAML already gives us real numbers and lists, so anything else is a mistake.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class LengthLimit(StrictModel):
    """Word-count limits for one channel."""

    min: int = Field(ge=1)
    max: int = Field(ge=1)

    @model_validator(mode="after")
    def min_below_max(self) -> Self:
        # Runs after the single fields are validated, so it can compare them.
        if self.min >= self.max:
            raise ValueError(f"min ({self.min}) must be less than max ({self.max})")
        return self


class PersonalityPair(StrictModel):
    """One `{is: ..., not: ...}` pair, e.g. reassuring, not patronising."""

    # `is` and `not` are Python keywords, so the fields get other names and read the YAML
    # keys through an alias. populate_by_name also allows PersonalityPair(is_=..., not_=...).
    model_config = ConfigDict(populate_by_name=True)

    is_: NonEmptyStr = Field(alias="is")
    not_: NonEmptyStr = Field(alias="not")

    @model_validator(mode="after")
    def is_differs_from_not(self) -> Self:
        if self.is_.casefold() == self.not_.casefold():
            raise ValueError(f"'is' and 'not' are the same: {self.is_!r}")
        return self


class Voice(StrictModel):
    personality: list[PersonalityPair] = Field(min_length=1)
    values: list[NonEmptyStr] = Field(min_length=1)
    principles: list[NonEmptyStr] = []


class Tone(StrictModel):
    """The four Nielsen Norman Group dimensions for one channel: 0 = first word, 1 = second."""

    funny_serious: Score
    formal_casual: Score
    respectful_irreverent: Score
    enthusiastic_matter_of_fact: Score


class ToneByChannel(StrictModel):
    social: Tone
    email: Tone
    web: Tone


class PerChannelInt(StrictModel):
    """A whole-number limit per channel, used for emoji_max, exclamation_max, hashtags_max."""

    social: NonNegativeInt
    email: NonNegativeInt
    web: NonNegativeInt


class PerChannelLength(StrictModel):
    social: LengthLimit
    email: LengthLimit
    web: LengthLimit


class Style(StrictModel):
    spelling: str = Field(pattern=r"^[a-z]{2}-[A-Z]{2}$")  # language-region, e.g. en-GB, fr-FR
    reading_grade_max: float = Field(ge=1, le=18)  # Flesch-Kincaid grade
    contractions: Literal["preferred", "allowed", "avoid"]
    apostrophe: Literal["straight", "curly"]
    emoji_max: PerChannelInt
    exclamation_max: PerChannelInt
    hashtags_max: PerChannelInt
    length_words: PerChannelLength


class GlossaryEntry(StrictModel):
    """The correct form of a term, and the wrong forms a check should flag."""

    term: NonEmptyStr
    wrong: list[NonEmptyStr] = Field(min_length=1)

    @model_validator(mode="after")
    def term_not_in_wrong(self) -> Self:
        # Otherwise the glossary check would flag every correct use of the term.
        if self.term in self.wrong:
            raise ValueError(f"{self.term!r} is listed as a wrong form of itself")
        return self


class Vocabulary(StrictModel):
    banned: list[NonEmptyStr] = Field(min_length=1)
    glossary: list[GlossaryEntry] = []

    @model_validator(mode="after")
    def no_duplicates(self) -> Self:
        # Banned words are matched case-insensitively, so compare them that way too.
        banned = [word.casefold() for word in self.banned]
        if dupes := sorted({w for w in banned if banned.count(w) > 1}):
            raise ValueError(f"duplicate banned words: {dupes}")
        terms = [entry.term for entry in self.glossary]
        if dupes := sorted({t for t in terms if terms.count(t) > 1}):
            raise ValueError(f"duplicate glossary terms: {dupes}")
        return self


class Example(StrictModel):
    off_brand: NonEmptyStr
    on_brand: NonEmptyStr

    @model_validator(mode="after")
    def texts_differ(self) -> Self:
        if self.off_brand == self.on_brand:
            raise ValueError("off_brand and on_brand are the same text")
        return self


class VoiceSpec(StrictModel):
    """The whole spec file."""

    brand: str = Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")  # an id such as brand-a
    name: NonEmptyStr
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")  # semantic version, e.g. 1.0.0
    tagline: NonEmptyStr
    voice: Voice
    tone_by_channel: ToneByChannel
    style: Style
    vocabulary: Vocabulary
    examples: list[Example] = Field(min_length=1)
