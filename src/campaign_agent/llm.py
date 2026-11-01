"""Chat and embedding models, all hosted on Microsoft Foundry.

- Writer: Claude Haiku 5.5 through Foundry's Anthropic endpoint (Messages API).
- Checker: GPT-6 Luna through Foundry's OpenAI-compatible v1 endpoint.
- Embeddings: text-embedding-3-large through the same v1 endpoint.

Writer and checker come from different model families, so the checker never judges
writing from its own family. This is the only module that knows about providers.
"""

from typing import Literal

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from campaign_agent.config import settings

Role = Literal["writer", "checker"]


def chat_model(role: Role = "writer") -> BaseChatModel:
    """The writer drafts and edits; the checker plans, checks, critiques and judges."""
    if role == "writer":
        return ChatAnthropic(
            model=settings.writer_deployment,
            base_url=settings.foundry_anthropic_endpoint,
            # Explicit keys, so machine-wide ANTHROPIC_* or OPENAI_* variables are never used.
            api_key=settings.foundry_api_key,
            max_tokens=16_000,
            # Haiku 5.5 thinks before answering by default; effort sets how much.
            reasoning_effort="medium",
        )
    return ChatOpenAI(
        model=settings.checker_deployment,
        base_url=settings.foundry_openai_endpoint,
        api_key=settings.foundry_api_key,
    )


def embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.embedding_deployment,
        dimensions=settings.embedding_dimensions,  # shortened from 3,072
        base_url=settings.foundry_openai_endpoint,
        api_key=settings.foundry_api_key,
        check_embedding_ctx_length=False,  # send plain text, not tiktoken token ids
    )
