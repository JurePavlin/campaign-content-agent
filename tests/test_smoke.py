"""Smoke tests: the package imports and models use the right deployments. No network calls."""

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

import campaign_agent
from campaign_agent import llm
from campaign_agent.config import settings


def test_package_version():
    assert campaign_agent.__version__


def test_models_use_deployment_for_role(monkeypatch):
    base = "https://example.services.ai.azure.com"
    monkeypatch.setattr(settings, "foundry_api_key", "test-key")
    monkeypatch.setattr(settings, "foundry_anthropic_endpoint", f"{base}/anthropic")
    monkeypatch.setattr(settings, "foundry_openai_endpoint", f"{base}/openai/v1/")
    monkeypatch.setattr(settings, "writer_deployment", "writer-model")
    monkeypatch.setattr(settings, "checker_deployment", "checker-model")

    writer = llm.chat_model("writer")
    checker = llm.chat_model("checker")

    assert isinstance(writer, ChatAnthropic) and writer.model == "writer-model"
    assert isinstance(checker, ChatOpenAI) and checker.model_name == "checker-model"
    assert llm.embeddings().dimensions == settings.embedding_dimensions
