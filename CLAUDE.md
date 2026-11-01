# CLAUDE.md

## Project

A LangGraph agent that turns a campaign brief into an approved, on-brand, claim-checked content pack (LinkedIn post, newsletter section, product blurb; EN, later FR). It checks hard brand rules in code, matches every claim against an evidence register, resists prompt injection, pauses for human approval and records provenance. The main result is an **ablation table** that shows what each component adds.

- Overview for humans: [README.md](README.md)
- **Architecture, workflow, data, evaluation and milestones: [docs/design.md](docs/design.md). Read it before starting work.**
- Prerequisites and Azure setup: [docs/setup.md](docs/setup.md)

This is a public portfolio project. The owner is an experienced data engineer (Python, SQL, PySpark, Azure, Microsoft Fabric) who is building it to learn and demonstrate AI agent engineering. When you introduce a concept they may not know yet (LangGraph `Send`, `interrupt()`, checkpointers, stores, LLM-judge calibration), explain it in two or three sentences, and say briefly why a design choice was made, so they can explain it in an interview.

## Current status

- **Done (1 Nov 2026):** repo, dependencies, settings (`config.py`), model clients (`llm.py`), smoke tests, CI, Postgres compose file, setup check script.
- **Waiting on the owner:** Azure Foundry resource and model deployments, then `.env` filled in.
- **Next:** Milestone 1, step 1: create Brand A (see docs/design.md, section 8).

Update this section at the end of each work session.

## Decisions

| Decision | Why |
|---|---|
| LangGraph, not Pydantic AI | Appears far more often in job postings. Pydantic is still used for every structured output |
| Azure OpenAI in Foundry via the **v1 API**, using `ChatOpenAI` with `base_url` | Azure skills matter in the target job market. The v1 API needs no `api_version`. Changing provider only touches `llm.py` |
| Writer `gpt-5.4`, checker `gpt-5.4-mini` | Cost routing: the small model plans, checks and judges. Deployment names are configurable in `.env` |
| LangSmith for tracing and evaluation datasets | Already set up; traces LangGraph with no extra code |
| One Postgres + pgvector container for everything | Checkpoints, memory store, claims register and exemplar index in one place. Simpler than adding Qdrant |
| Tools as plain Python functions first, MCP servers in Milestone 3 | Keeps the MVP small. Write tools behind a small interface so they can move to MCP later |
| Hand-written voice spec in the MVP | Spec extraction from the corpus comes in Milestone 3 |
| Python 3.13, uv, ruff, pytest, MIT licence | |

Record new decisions here with a one-line reason.

## Conventions

- **Every LLM output is a Pydantic model**, enforced with `with_structured_output`.
- **Hard rules live in code**, never only in a prompt. Each rule check has unit tests with passing and failing examples.
- **Untrusted text** (the brief, web content, corpus texts) goes into clearly delimited data sections of a prompt, never into the instructions.
- Get models from `campaign_agent.llm.chat_model("writer" | "checker")`; don't construct clients elsewhere.
- Unit tests make no network calls. Tests that call Azure or Postgres are marked `@pytest.mark.integration` and are skipped by default.
- **Never invent results.** The README's Results section only shows numbers produced by the evaluation code.
- Synthetic data is labelled as synthetic.
- Never commit `.env` or keys. Keep the owner's personal information out of the repo.
- Small commits with clear messages. Run `uv run ruff format .` and `uv run ruff check .` before committing.

## Commands

The owner uses Windows 11 and PowerShell.

```bash
uv sync                                   # install or update dependencies
uv add <package>                          # add a dependency
docker compose up -d                      # start Postgres + pgvector (Docker Desktop must be running)
uv run pytest                             # unit tests
uv run pytest -m integration              # tests that call Azure or Postgres
uv run ruff check . ; uv run ruff format .
uv run python scripts/check_setup.py      # verify Azure, Postgres and LangSmith
uv run langgraph dev                      # LangGraph Studio (needs a langgraph.json pointing at the graph)
```
