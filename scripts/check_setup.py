"""Check that the local setup works: settings, Azure OpenAI deployments, Postgres and LangSmith.

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


def settings_present() -> str:
    missing = [
        n for n in ("azure_openai_endpoint", "azure_openai_api_key") if not getattr(settings, n)
    ]
    if missing or "<your-resource>" in settings.azure_openai_endpoint:
        raise ValueError(f"fill in .env: {', '.join(missing) or 'azure_openai_endpoint'}")
    return settings.azure_openai_endpoint


def python_version() -> str:
    return sys.version.split()[0]  # requires-python in pyproject.toml enforces 3.13+


def chat(role: llm.Role) -> str:
    model = llm.chat_model(role)
    reply = model.invoke("Reply with the single word OK.")
    return f"{model.model_name} replied {reply.content!r}"


def embed() -> str:
    vector = llm.embeddings().embed_query("brand voice")
    return f"{settings.embedding_deployment} returned {len(vector)} dimensions"


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
check("Azure settings in .env", settings_present)
if results[-1][1]:
    check("Azure writer deployment", lambda: chat("writer"))
    check("Azure checker deployment", lambda: chat("checker"))
    check("Azure embedding deployment", embed)
check("Postgres + pgvector", postgres)
check("LangSmith", langsmith)

for name, ok, detail in results:
    print(f"[{'OK' if ok else 'FAIL':4}] {name}: {detail}")
sys.exit(0 if all(ok for _, ok, _ in results) else 1)
