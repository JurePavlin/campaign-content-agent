"""Load a brand's voice spec from YAML into a validated VoiceSpec."""

from pathlib import Path

import yaml

from campaign_agent.spec.models import VoiceSpec

DATA_DIR = Path(__file__).parents[3] / "data"
BRAND_A_SPEC = DATA_DIR / "brands/brand_a/voice_spec.yaml"


def load_spec(path: str | Path = BRAND_A_SPEC) -> VoiceSpec:
    """Read and validate a voice spec. Raises pydantic.ValidationError if it's malformed.

    yaml.safe_load only builds plain data (dicts, lists, strings, numbers). yaml.load can
    build arbitrary Python objects from tags in the file, so a hostile file could run code.
    """
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return VoiceSpec.model_validate(raw)
