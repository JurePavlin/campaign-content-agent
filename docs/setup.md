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
| **Azure OpenAI in Foundry** | The LLMs | **To do, see step 1** |

## 1. Azure OpenAI in Microsoft Foundry (one-off, about 20 minutes)

1. **Use a personal Azure subscription**, not an employer's.
2. **Set a budget alert first:** Cost Management → Budgets, for example €20 a month with alerts at 50%, 90% and 100%.
3. **Create a Microsoft Foundry resource** in the Azure portal or at [ai.azure.com](https://ai.azure.com):
   - Resource group: `rg-campaign-agent`
   - Region: **Sweden Central** (EU)
4. **Deploy three models** and note each deployment name:

   | Deployment | Role | Model |
   |---|---|---|
   | `gpt-5.4` | Writer and editor | GPT-5.4 |
   | `gpt-5.4-mini` | Planner, checks, judge | GPT-5.4 mini |
   | `text-embedding-3-small` | Exemplar retrieval | text-embedding-3-small |

   - Deployment type: **Global Standard** is cheapest. **Data Zone Standard (EU)** keeps processing in the EU, which is a useful data-residency talking point.
   - A low tokens-per-minute quota is enough.
   - If a model isn't offered to your subscription, deploy the closest available one and put its deployment name in `.env`.
5. **Copy the endpoint and a key** into `.env`. The endpoint must end in `/openai/v1/`, for example `https://<resource>.openai.azure.com/openai/v1/`.

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
| `langchain-openai` | Chat and embedding clients for the Azure v1 endpoint |
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
| `scikit-learn` | 2 | Brand-fit classifier |
| `spacy` + `en_core_web_sm` | 3 | Stylometrics for spec extraction |
| `mcp`, `langchain-mcp-adapters` | 3 | MCP servers for catalogue, claims and CMS |
| `fastapi`, `uvicorn` | 3 | API |
| `streamlit` | 3 | Review screen |
| `datasketch` | 3 | Near-duplicate removal for the GOV.UK corpus |

## 5. Building with Claude Code

Open a new Claude Code session with `D:\coding\campaign-content-agent` as the folder. `CLAUDE.md` loads automatically. A good first message:

> Read CLAUDE.md and docs/design.md, then let's start Milestone 1, step 1: creating Brand A.
