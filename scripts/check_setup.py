"""Check that the local setup works: settings, Foundry deployments, Postgres and LangSmith.

Run with: uv run python scripts/check_setup.py
"""

import os
import sys

import psycopg

from campaign_agent import llm
from campaign_agent.config import settings

results: list[tuple[str, bool, str]] = []


def check(name: str, fn) -> None:
    try:
        results.append((name, True, fn()))
    except Exception as exc:  # report every failure, keep checking the rest
        results.append((name, False, f"{type(exc).__name__}: {exc}"[:200]))


def settings_present(*names: str) -> str:
    missing = [
        n for n in names if not getattr(settings, n) or "<your-resource>" in getattr(settings, n)
    ]
    if missing:
        raise ValueError(f"fill in .env: {', '.join(n.upper() for n in missing)}")
    return getattr(settings, names[1])  # the base URL


def python_version() -> str:
    return sys.version.split()[0]  # requires-python in pyproject.toml enforces 3.13+


def chat(role: llm.Role) -> str:
    model = settings.writer_model if role == "writer" else settings.checker_model
    reply = llm.chat_model(role).invoke("Reply with the single word OK.")
    return f"{model} replied {reply.text!r}"  # .text skips Claude's thinking blocks


def embed() -> str:
    vector = llm.embeddings().embed_query("brand voice")
    if len(vector) != settings.embedding_dimensions:
        raise ValueError(f"expected {settings.embedding_dimensions} dimensions, got {len(vector)}")
    return f"{settings.embedding_model} returned {len(vector)} dimensions"


def postgres() -> str:
    with psycopg.connect(settings.database_url, connect_timeout=5) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        version = conn.execute(
            "SELECT extversion FROM pg_extension WHERE extname = 'vector'"
        ).fetchone()
        return f"connected, pgvector {version[0]}"


def langsmith() -> str:
    if not os.getenv("LANGSMITH_API_KEY"):
        raise ValueError("LANGSMITH_API_KEY is not set")
    tracing = os.getenv("LANGSMITH_TRACING", "false")
    return f"tracing={tracing}, project={os.getenv('LANGSMITH_PROJECT')}"


check("Python 3.13+", python_version)
check(
    "Claude settings in .env",
    lambda: settings_present("anthropic_foundry_api_key", "anthropic_foundry_base_url"),
)
if results[-1][1]:
    check("Writer model (Claude)", lambda: chat("writer"))
check(
    "OpenAI settings in .env",
    lambda: settings_present("openai_foundry_api_key", "openai_foundry_base_url"),
)
if results[-1][1]:
    check("Checker model (GPT-6 Luna)", lambda: chat("checker"))
    check("Embedding model", embed)
check("Postgres + pgvector", postgres)
check("LangSmith", langsmith)

for name, ok, detail in results:
    print(f"[{'OK' if ok else 'FAIL':4}] {name}: {detail}")
sys.exit(0 if all(ok for _, ok, _ in results) else 1)
