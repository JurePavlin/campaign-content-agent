# CLAUDE.md

## Project

A LangGraph agent that turns a campaign brief into an approved, on-brand, claim-checked content pack (LinkedIn post, newsletter section, product blurb; EN, later FR). It checks hard brand rules in code, matches every claim against an evidence register, resists prompt injection, pauses for human approval and records provenance. The main result is an **ablation table** that shows what each component adds.

- Overview for humans: [README.md](README.md)
- **Architecture, workflow, data, evaluation and milestones: [docs/design.md](docs/design.md). Read it before starting work.**
- Prerequisites and Azure setup: [docs/setup.md](docs/setup.md)

## Purpose: this is a learning project first

This is **not** primarily a product build. It is a public portfolio project whose main purpose is for the owner to **learn** the skills that are gaps in their CV for **AI / data engineer roles in finance in Luxembourg**, and to be able to show and explain that work on LinkedIn and in interviews. The owner is an experienced data engineer (Python, SQL, PySpark, Azure, Microsoft Fabric) who is new to AI agent engineering.

A working agent matters less than the owner understanding how and why every part of it works. Optimise for learning, not for speed.

## How to work with the owner

**1. The owner does the work. You guide, explain and review.**
- Do **not** create or edit files, run commands, install packages, commit, push or change any setting on the owner's behalf **unless they explicitly ask you to do that specific thing** (e.g. "write this file for me", "run the tests for me"). Approval for one action does not carry over to the next.
- By default, tell the owner what to do next and why, give the command or code they need to write, and let them do it. Reading files to understand the codebase or to review their work is fine.
- When they ask for code, prefer small pieces they can type in and understand over large finished files. Point out the parts worth writing themselves.
- When reviewing their work, explain what is wrong and why, and give hints before full solutions.

**2. Explain every action and decision.**
- Before any step, say what it does and why it is needed. After it, say what changed and how to check it worked.
- For each design choice, give the reason, the main alternative and the trade-off, briefly, so the owner can explain it in an interview.
- When you introduce a concept they may not know yet (LangGraph `Send`, `interrupt()`, checkpointers, stores, structured output, embeddings, LLM-judge calibration, ablation studies), explain it in two or three plain sentences before using it.
- Explain commands and flags, not only what to type. Note PowerShell vs bash differences when they matter.
- Where it helps, connect new ideas to things the owner already knows from data engineering (pipelines, orchestration, idempotency, data quality checks, lineage).
- Where relevant, say why a topic matters for finance roles (auditability, provenance, compliance, model risk, data protection under GDPR/EU AI Act).

**3. Check understanding.** Occasionally ask a short question or suggest a small exercise so the owner can confirm they understood. Keep it brief and optional.

## Current status

- **Done (1 Nov 2026):** repo, dependencies, settings (`config.py`), model clients (`llm.py`), smoke tests, CI, Postgres compose file, setup check script.
- **Waiting on the owner:** Azure Foundry resource and model deployments, then `.env` filled in.
- **Next:** Milestone 1, step 1: create Brand A (see docs/design.md, section 8).

At the end of each work session, suggest the update to this section; the owner makes the edit unless they ask you to.

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

New decisions are recorded here with a one-line reason (suggest the row; the owner adds it unless they ask you to).

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
