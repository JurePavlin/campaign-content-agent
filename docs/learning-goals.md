# Learning goals

This project exists to **learn** the skills that Data & AI Engineer roles in Luxembourg's financial sector ask for, and to be able to explain them in interviews. A polished product comes second. Read this before planning any work, and use it to decide what to build and how.

## 1. Where the owner starts

**Already proven at work, so build on these rather than re-teach them:**
- Python, SQL and PySpark; lakehouse pipelines and data modelling on Microsoft Fabric; Power BI.
- Data quality and governance (Purview, GDPR); Azure architecture and security.
- RAG with Azure AI Search, agents built in Microsoft Foundry, and document AI in production.
- Six years in a regulated financial-services environment (KYC, AML, audits).

**New:** building agents in code with a framework, software-engineering practice around AI systems, and measuring whether an AI system actually works.

Connect new ideas to data engineering where it helps:

| New idea | Data-engineering equivalent |
|---|---|
| LangGraph graph with shared state | An orchestrated pipeline passing a context object between tasks |
| Checkpointer | Restartable, idempotent pipeline runs |
| Evaluation suite | Data quality tests, but for model outputs |
| Provenance record | Data lineage |
| Embedding index | An index built for similarity lookups instead of exact matches |

## 2. What the job market asks for

From 17 Luxembourg Data and AI job postings reviewed in October 2026. The counts are lower bounds.

| Skill | Postings | Starting point | Where this project covers it |
|---|---|---|---|
| Python | 13 | Strong | Throughout |
| SQL | 11 | Strong | pgvector queries, claims register |
| LLMs / GenAI | 8 | Good | Throughout |
| Agents | 7 | Good (Foundry and Fabric agents) | **Core: LangGraph in code** |
| REST APIs | 7 | Gap | Milestone 3: FastAPI |
| Classical ML | 7 | Gap | Small: brand-fit classifier, Milestone 2 |
| RAG | 6 | Good | **Exemplar retrieval on pgvector** |
| Automated testing | 5 | Gap | **pytest for every rule and check** |
| CI/CD | 5 | Gap | **GitHub Actions with quality gates** |
| MLOps | 5 | Gap | Not here (see section 4) |
| LLM evaluation | 4 | Gap | **Core: judge, ablation, red-team** |
| Docker | 3 | Basic | Docker Compose |
| LangChain / LangGraph | 2 | Familiar | **Core** |
| Vector databases | 1 | Gap | pgvector |

## 3. The gaps this project must close

Eight gaps were ranked by local demand and size. This project targets four of them: **2, 3, 6 and 7**. For each: what to practise, the evidence it leaves in the repo, and what the owner should be able to explain.

### Gap 2: engineering practice (tests, CI/CD, APIs, Docker)

- **Practise:**
  - Unit tests for every rule check, with passing and failing examples.
  - Integration tests marked separately.
  - GitHub Actions running lint and tests, and evaluation gates from Milestone 2.
  - Docker Compose for services; FastAPI in Milestone 3.
- **Evidence:** CI badge, test suite, a CI run that blocked a regression.
- **Explain:** what to unit-test in an LLM system and what to evaluate instead; why LLM calls are faked in unit tests; how a quality gate works in CI.

### Gap 3: LLM evaluation and observability

- **Practise:**
  - A golden set with a held-out split.
  - An LLM judge with a rubric, calibrated against hand ratings (Cohen's kappa or Spearman correlation).
  - The ablation table.
  - Red-team attack success rate, and consistency across 5 runs of the same brief.
  - Retrieval recall@4.
  - LangSmith tracing, and cost per approved piece.
- **Evidence:** the README results table, produced by code.
- **Explain:** why an uncalibrated judge can't be trusted; self-preference bias; test-set leakage; offline versus online evaluation.

### Gap 6: agent frameworks and multi-agent design

- **Practise:**
  - LangGraph state, nodes, conditional edges and retry loops.
  - `Send` for parallel writers and `interrupt()` for human approval.
  - The Postgres checkpointer, then the long-term store and MCP servers built yourself in Milestone 3.
- **Build the graph explicitly.** Don't use prebuilt agents such as `create_react_agent` that hide the mechanics.
- **Explain:** workflow versus agent; why hard rules run as deterministic code; how a run resumes from a checkpoint after human approval.

### Gap 7: advanced retrieval

- **Practise:**
  - Embeddings, pgvector, an HNSW index and metadata filters.
  - **Write the SQL by hand first,** before trying `langchain-postgres`.
  - Recall@k evaluation, comparing two embedding models.
- **Explain:** why embeddings capture topic but not tone; Postgres with pgvector versus a dedicated vector database; the trade-offs of dimensions and index types; why changing the embedding model means re-embedding everything.

### Cross-cutting skills valued in finance roles

- **Provenance and audit trail:** who approved what, with which model and which voice-spec version.
- **Compliance by design:** the claims register, EU Directive 2024/825 on environmental claims, EU AI Act transparency rules (Article 50).
- **Security:** prompt injection, least-privilege tools.
- **Cost control:** model routing, prompt caching, cost per approved piece.

## 4. Out of scope for this project

These gaps are real, but they belong to separate portfolio projects. Don't add them here, even when it looks convenient.

| Gap | Covered by |
|---|---|
| 1. Production ML and MLOps (training, MLflow, serving, drift) | A separate AML risk-model project |
| 4. Databricks | A separate transaction-monitoring lakehouse project |
| 5. Airflow and dbt | The same lakehouse project |
| 8. Knowledge graphs and ontologies | Separate KYC and fund-administration agent projects |
| Microsoft Agent Framework | The KYC agent project |
| Fine-tuning, Kubernetes, Terraform, Kafka | At most a stretch goal |

Also out of scope: a polished front end, a production deployment and any real customer or employer data.

## 5. Staying on course

Rules for every session:

1. **[docs/design.md](design.md) is the plan.** Follow its milestones in order. No Milestone 3 stretch goals before Milestones 1 and 2 are done.
2. **Changing the design is fine; drifting silently isn't.** If a better approach comes up, stop and discuss it with the owner: what changes, why, and which learning goal in section 3 it serves. If the owner agrees, record it in CLAUDE.md's Decisions table and update docs/design.md.
3. **Choose the approach that teaches the target skill,** not the quickest one. For example: hand-written SQL before an abstraction, an explicit LangGraph graph rather than a prebuilt agent, and a rubric you write and calibrate yourself rather than a library's ready-made score.
4. **Every new library or service needs a reason** tied to a goal in section 3. Ask the owner before adding one.
5. **No result without evidence.** Numbers in the README come from the evaluation code.
6. **End each milestone with an "explain it" check:** the owner answers that milestone's questions from section 6 in their own words.

## 6. Questions the owner should be able to answer

**After Milestone 1:**
- How do you turn "tone of voice" into something you can measure?
- Why enforce hard rules in code rather than in the prompt? How does the retry loop work?
- How does the human-approval pause work, and where is the state while the run waits?
- How do you find on-brand examples, and why don't embeddings alone capture tone?
- What did each component add? (Show the ablation table.)
- Why do the writer and the judge come from different model families?

**After Milestone 2:**
- How do you know the LLM judge agrees with humans?
- How do you defend against prompt injection, and how did you measure it?
- What does CI check, and what would block a release?
- How consistent is the agent across repeated runs of the same brief?

**By the end:**
- Why LangGraph rather than Pydantic AI or Microsoft Agent Framework?
- What does an approved piece cost, and how would you reduce it?
- What do the EU AI Act and the Green Transition Directive change for AI-generated marketing?
- What would you change to run this in production at a bank?

## 7. Definition of done for the portfolio

- **README:** problem, architecture diagram, one-command start, results table, decisions and trade-offs, what's next.
- **Tests and CI:** pytest, ruff, type hints and a CI badge.
- **A 2-minute demo video.**
- **One LinkedIn post** about one lesson learned, for example "Why your AI doesn't sound like your brand, and how to measure it".
- **CV and LinkedIn wording uses only real numbers** from the results table.
