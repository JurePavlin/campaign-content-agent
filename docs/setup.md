# Setup

Everything needed to run and develop the project on Windows 11.

## Checklist

| Item | Purpose | Status (1 Nov 2026) |
|---|---|---|
| Git 2.51 | Version control | Installed, identity set |
| GitHub CLI 2.103 | Repo, PRs, CI from the terminal | Installed. Run `gh auth login` once |
| Python 3.13 | Runtime | Installed |
| uv | Packages, virtual env, lock file | Installed. Open a new terminal so it's on PATH |
| Docker Desktop 28.4 | Postgres + pgvector | Installed. Must be running for the database |
| VS Code | Editor | Installed. Add the *Python* and *Ruff* extensions |
| Azure CLI 2.87 | Keyless Azure auth later | Installed (optional for now) |
| Node.js 22 | Some MCP servers run with `npx` (Milestone 3) | Installed |
| LangSmith | Tracing and evaluation | API key set machine-wide; project set in `.env` |
| **Microsoft Foundry models** | Writer, checker and embeddings | **To do, see step 1** |
| Ollama (optional) | Local model comparison, Milestone 1 step 7 | Not installed yet |

## 1. Microsoft Foundry (one-off, about 30 minutes)

1. **Use a personal Azure subscription with a pay-as-you-go payment method** (a card on file), not an employer's. Claude models aren't available on free-trial, student or credit-only subscriptions.
2. **Set a budget alert first:** Cost Management → Budgets, for example €10 a month with alerts at 50%, 90% and 100%. Expected spend for Milestone 1 is a few dollars.
3. **Create a Microsoft Foundry resource and project** at [ai.azure.com](https://ai.azure.com):
   - Resource group: `rg-campaign-agent`
   - Region: **Sweden Central** (EU). If a model isn't offered there, its model card lists the supported regions.
4. **Deploy three models**, keeping each model's name as the deployment name:

   | Deployment | Role | Price per 1M tokens (input / output) |
   |---|---|---|
   | `claude-haiku-5-5` | Writer and editor | $0.10 / $0.50 |
   | `gpt-6-luna` | Planner, checks, critic, judge | $0.10 / $0.50 |
   | `text-embedding-3-large` | Exemplar retrieval | $0.13 (input only) |

   - **Claude is sold through Azure Marketplace:** you accept Anthropic's Marketplace terms when you deploy it. Claude uses the **Global Standard** deployment type.
   - **GPT-6 Luna and the embedding model:** **Global Standard** is cheapest. **Data Zone Standard (EU)** keeps processing in the EU for about 10% more, which is a useful data-residency talking point.
   - **Quota:** some subscription types start with zero quota for some models. Check each deployment's quota and request an increase if needed; a low tokens-per-minute quota is enough.
5. **Copy the key and both endpoints into `.env`.** One key covers every deployment in the resource:
   - Claude: `https://<resource>.services.ai.azure.com/anthropic`
   - OpenAI models: `https://<resource>.services.ai.azure.com/openai/v1/`

   Each deployment's details page shows its target URI if yours look different.

Later hardening (good for interviews): switch from API keys to Entra ID keyless auth with `az login` and `DefaultAzureCredential`.

## 2. GitHub

```bash
gh auth login
```

Choose GitHub.com, HTTPS, and log in with the browser. The repo is `campaign-content-agent` (public).

## 3. Local environment

```bash
uv sync
copy .env.example .env
docker compose up -d
uv run python scripts/check_setup.py
uv run pytest
```

`check_setup.py` reports OK or FAIL for Python, the Azure settings, each Azure deployment, Postgres with pgvector, and LangSmith.

**Note:** `LANGSMITH_TRACING=true` is set machine-wide, so every LangChain program on this machine sends traces to LangSmith. This project's `.env` sends them to the `campaign-content-agent` project.

## 4. Libraries

**Installed now** (`pyproject.toml`):

| Package | Purpose |
|---|---|
| `langgraph` | The agent graph: state, nodes, loops, `Send`, `interrupt()` |
| `langgraph-checkpoint-postgres` | Saves graph state in Postgres (human approval, replay) |
| `langchain-anthropic` | Claude client for Foundry's Anthropic endpoint |
| `langchain-openai` | GPT-6 Luna and embedding clients for Foundry's OpenAI v1 endpoint |
| `langchain-postgres` | pgvector store for the exemplar index |
| `psycopg[binary]` | Postgres driver |
| `pydantic-settings`, `python-dotenv` | Settings from `.env` |
| `pyyaml` | Voice spec and data files |
| `textstat` | Reading-level checks |
| `pytest`, `ruff` (dev) | Tests, linting and formatting |
| `langgraph-cli[inmem]` (dev) | `langgraph dev`: LangGraph Studio for visual debugging |

**Add later, when a milestone needs them** (`uv add <package>`):

| Package | Milestone | Purpose |
|---|---|---|
| `langchain-ollama`, plus Ollama itself | 1 (step 7) | gpt-oss:20b on a local 16 GB GPU, for the model comparison |
| `scikit-learn` | 2 | Brand-fit classifier |
| `spacy` + `en_core_web_sm` | 3 | Stylometrics for spec extraction |
| `mcp`, `langchain-mcp-adapters` | 3 | MCP servers for catalogue, claims and CMS |
| `fastapi`, `uvicorn` | 3 | API |
| `streamlit` | 3 | Review screen |
| `datasketch` | 3 | Near-duplicate removal for the GOV.UK corpus |

## 5. Building with Claude Code

Open a new Claude Code session with `D:\coding\campaign-content-agent` as the folder. `CLAUDE.md` loads automatically. A good first message:

> Read CLAUDE.md and docs/design.md, then let's start Milestone 1, step 1: creating Brand A.
