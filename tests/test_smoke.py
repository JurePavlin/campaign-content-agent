"""Smoke tests: the package imports and models use the right deployments. No network calls."""

import campaign_agent
from campaign_agent import llm
from campaign_agent.config import settings


def test_package_version():
    assert campaign_agent.__version__


def test_chat_model_uses_deployment_for_role(monkeypatch):
    monkeypatch.setattr(
        settings, "azure_openai_endpoint", "https://example.openai.azure.com/openai/v1/"
    )
    monkeypatch.setattr(settings, "azure_openai_api_key", "test-key")
    monkeypatch.setattr(settings, "writer_deployment", "big-model")
    monkeypatch.setattr(settings, "checker_deployment", "small-model")

    assert llm.chat_model("writer").model_name == "big-model"
    assert llm.chat_model("checker").model_name == "small-model"
