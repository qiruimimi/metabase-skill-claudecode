---
name: kmb-metabase
description: Root Claude Code skill for the internal KMB (Metabase) platform. Use it when the user needs general KMB help, needs routing to a specific kmb-* skill, or needs shared KMB references, rules, search tools, or space-data context.
---

# KMB Metabase

Use this as the root navigation skill for the KMB skill family. This skill does not own end-to-end execution; it routes work to the right `kmb-*` skill and exposes shared references.

## When to use

- The user asks for general KMB or Metabase help without saying whether they want query, modeling, visualization, dashboard, or migration work.
- You need shared references, API rules, MBQL guidance, or offline space-data.
- You need to decide which `kmb-*` skill should handle the task.

## Routing

Route quickly and only load the next skill that matches the task.

- Search Space page, graph, or SQL: use `/kmb-space-query`
- Analyze SQL and design model/question: use `/kmb-sql-analyzer`
- Create or update a collection: use `/kmb-collection-builder`
- Create a model: use `/kmb-model-builder`
- Create MBQL questions: use `/kmb-question-builder`
- Configure chart visualization: use `/kmb-viz-config`
- Build dashboards and parameter mappings: use `/kmb-dashboard-builder`
- Run full Space to KMB migration: use `/kmb-migration`

## Progressive loading

Keep context small.

1. Read the target skill's `SKILL.md` first.
2. Only read shared references when they are needed.
3. Do not preload all rules, references, and data for a simple task.

Read these shared resources on demand:

- API details: `references/api-reference.md`
- MBQL patterns: `references/mbql-best-practices.md`
- Real collection patterns: `references/collection-patterns.md`
- Dashboard parameter mapping patterns: `references/parameter-mapping-patterns.md`
- Dashboard configuration rules: `references/dashboard-configs.md`
- Migration workflow details: `references/migration-guide.md`
- Skill hand-off contract: `references/skill-handoffs.md`
- Guardrails and failure rules: `references/rules/`
- Offline page and graph mappings: `space-data/`

## Shared tools

- `scripts/search_kmb.py`: search KMB content
- `scripts/query_card.py`: query a card directly
- `scripts/inspect_collection.py`: summarize collection composition, card query modes, and dashboard parameter mapping patterns
- `scripts/core/`: lightweight HTTP/config/error helpers
- `scripts/lib/kmb/`: shared Python package used by create/update scripts in sibling skills

## Notes

- Child skills do not need this skill to be explicitly activated first.
- If docs disagree, prefer `references/rules/*`, then the active skill's `SKILL.md`, then other references.
- Prefer direct Metabase API usage or the bundled scripts. Do not introduce a new heavyweight SDK.
- For multi-step work, prefer following `references/skill-handoffs.md` instead of ad-hoc switching.
