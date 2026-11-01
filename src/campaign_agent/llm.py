"""Chat and embedding models on Azure OpenAI (Microsoft Foundry) through the v1 API.

The v1 API is OpenAI-compatible, so the standard LangChain OpenAI classes work with the
Azure endpoint as base_url and the deployment name as the model. Switching provider later
means changing only this module.
"""

from typing import Literal

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from campaign_agent.config import settings

Role = Literal["writer", "checker"]


def chat_model(role: Role = "writer") -> ChatOpenAI:
    """The writer is the larger model; the checker is a small, cheap one for checks and judging."""
    deployment = settings.writer_deployment if role == "writer" else settings.checker_deployment
    return ChatOpenAI(
        model=deployment,
        base_url=settings.azure_openai_endpoint,
        # Explicit, so a machine-wide OPENAI_API_KEY is never used.
        api_key=settings.azure_openai_api_key,
    )


def embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.embedding_deployment,
        base_url=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        check_embedding_ctx_length=False,  # send plain text, not tiktoken token ids
    )
