"""Smoke tests: the package imports and models use the right settings. No network calls."""

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

import campaign_agent
from campaign_agent import llm
from campaign_agent.config import settings


def test_package_version():
    assert campaign_agent.__version__


def test_models_use_settings_for_role(monkeypatch):
    base = "https://example.services.ai.azure.com"
    monkeypatch.setattr(settings, "anthropic_foundry_api_key", "claude-key")
    monkeypatch.setattr(settings, "anthropic_foundry_base_url", f"{base}/anthropic")
    monkeypatch.setattr(settings, "writer_model", "writer-model")
    monkeypatch.setattr(settings, "openai_foundry_api_key", "openai-key")
    monkeypatch.setattr(settings, "openai_foundry_base_url", f"{base}/openai/v1/")
    monkeypatch.setattr(settings, "checker_model", "checker-model")

    writer = llm.chat_model("writer")
    checker = llm.chat_model("checker")

    assert isinstance(writer, ChatAnthropic) and writer.model == "writer-model"
    assert writer.anthropic_api_key.get_secret_value() == "claude-key"
    assert isinstance(checker, ChatOpenAI) and checker.model_name == "checker-model"
    assert checker.openai_api_key.get_secret_value() == "openai-key"
    assert llm.embeddings().dimensions == settings.embedding_dimensions
