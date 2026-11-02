# Data

Brand data, briefs and evaluation sets. See [docs/design.md](../docs/design.md), section 2.

- `brands/brand_a/`: the fictional brand (synthetic): style guide, voice spec, corpus, catalogue, claims register.
- `briefs/`: golden briefs (development and held-out) and the red-team set.
- `raw/`: downloaded source data such as the GOV.UK corpus. Git-ignored; recreated by scripts.

## Brand A: Moien Vëlo (synthetic)

**Everything about Brand A is synthetic:** the company, its products, people, customers, prices, claims and evidence documents are invented. Real places in Luxembourg appear only as settings. The one real reference is the EU legislation cited in `claims.yaml`.

| File | Contents |
|---|---|
| `style_guide.md` | The brand rules for humans: audience, voice, tone, style, banned words, glossary, claims policy |
| `voice_spec.yaml` | The same rules in machine-readable form, for the spec model and rule checks |
| `catalogue.yaml` | 6 products with specs and prices (including the Stroller's price history) |
| `claims.yaml` | 33 claims: 23 approved with evidence and validity dates, 10 not substantiated |
| `corpus.jsonl` | 150 approved texts, March 2024 to October 2026: 60 social, 40 email, 50 web |
| `../briefs/golden.jsonl` | 30 golden briefs: 20 development, 10 held-out |

**Facts rule:** a draft may only state facts found in `catalogue.yaml` or in an approved, currently valid claim in `claims.yaml`.

### Provenance

Generated on 2 November 2026 by Claude Opus 5.5 in Claude Code, from the owner's brief (brand name, audience, positioning and tone). Not yet reviewed line by line by the owner.

The agent's writer is Claude Haiku 5.5, from the same model family as the generator. Exemplars written by a related model may make the writer's output look more on-brand than it would against human-written texts. This is a known limitation, recorded here so the evaluation can mention it.

### Deliberate traps

These are intentional, so the checks and evaluation have something to catch:

- **Outdated prices in the corpus.** Texts from before March 2026 quote the Stroller at €2,690. The current price is €2,890. Retrieval may surface old exemplars; the writer must take prices from the catalogue, not from examples.
- **Expired and dated claims.** CL-023 (€200 off the Gentle Climber) expired on 31 May 2026. CL-022 (free panniers) expires on 30 November 2026. Home test rides (CL-021) and battery take-back (CL-015) only exist from 2025.
- **Unsubstantiated claims.** CL-024 to CL-033 are listed with status `not_substantiated` so the claims check can recognise and block them.
- **Trap briefs.** 18 golden briefs contain a trap. Most ask for something the agent must refuse or correct: banned words, generic environmental claims, health claims, expired offers or invented specs. Each lists its `traps` and the `blocked_claims` it should trigger.
- **Mentions that aren't claims.** Three corpus texts (from 28 and 29 September 2026) discuss the EU rules on environmental claims without making one. A good claims check must tell the difference.
