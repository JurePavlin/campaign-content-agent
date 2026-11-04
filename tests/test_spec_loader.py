"""Unit tests for load_spec. Local files only, no network calls."""

import pytest
from pydantic import ValidationError

from campaign_agent.spec.loader import BRAND_A_SPEC, load_spec
from campaign_agent.spec.models import VoiceSpec


def test_loads_brand_a_by_default():
    spec = load_spec()
    assert isinstance(spec, VoiceSpec)
    assert spec.name == "Moien Vëlo"  # also proves the file is read as UTF-8


def test_accepts_a_string_path():
    assert load_spec(str(BRAND_A_SPEC)).brand == "brand-a"


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_spec(tmp_path / "missing.yaml")


def test_invalid_spec_raises_validation_error(tmp_path):
    # tmp_path is a fresh temporary folder that pytest creates for this test.
    bad = tmp_path / "voice_spec.yaml"
    bad.write_text("brand: brand-a\nname: Test\n", encoding="utf-8")
    with pytest.raises(ValidationError):
        load_spec(bad)


def test_empty_file_raises_validation_error(tmp_path):
    empty = tmp_path / "voice_spec.yaml"
    empty.write_text("", encoding="utf-8")  # safe_load returns None for an empty file
    with pytest.raises(ValidationError):
        load_spec(empty)


def test_python_tags_are_not_executed(tmp_path):
    # yaml.load would try to build this object; safe_load refuses.
    hostile = tmp_path / "voice_spec.yaml"
    hostile.write_text("!!python/object/apply:os.system ['echo hacked']\n", encoding="utf-8")
    with pytest.raises(Exception, match="python/object"):
        load_spec(hostile)
