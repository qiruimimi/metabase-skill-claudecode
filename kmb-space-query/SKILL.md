---
name: kmb-space-query
description: Query the internal Space dataset used by KMB migration. Use it to search pages, inspect a page or graph, extract a graph's SQL, or browse the offline tree before any modeling or migration work.
argument-hint: "[search|page|graph|sql|tree] ..."
---

# KMB Space Query

Use this skill for upstream Space discovery only.

## Inputs

Use whichever identifier the user already gave.

- `keyword` for `search`
- `page_id` for `page`
- `graph_id` for `graph` or `sql`
- `tree` intent for browsing the directory tree

If the user already gave a `page_id` or `graph_id`, do not ask follow-up questions before running the matching query.

## Commands

Run the bundled script with `${CLAUDE_SKILL_DIR}` so it works from any current working directory.

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/space_sql_mapper.py" search "转化"
python3 "${CLAUDE_SKILL_DIR}/scripts/space_sql_mapper.py" page 34433
python3 "${CLAUDE_SKILL_DIR}/scripts/space_sql_mapper.py" graph 41236
python3 "${CLAUDE_SKILL_DIR}/scripts/space_sql_mapper.py" sql 41236
python3 "${CLAUDE_SKILL_DIR}/scripts/space_sql_mapper.py" tree
```

## Source priority

For normal migration discovery, use sources in this order:

1. live Tesseract MCP for page, graph, query, parameter, and path truth
2. local offline JSON under `data/` only when MCP lacks the needed shape or detail

Treat offline data as a supplement, not the default authority, when MCP is available.

## Practical rules

- For SQL graphs, prefer MCP `get_graph` / `get_query` first.
- If a local fallback is needed, the common offline SQL field is `displayGraphList[*].graph.executedSql`, not a guaranteed `query.committedSql`.
- For `TEXT` graphs, MCP may return “暂不支持语义化解析”. In that case, read the original HTML from offline `page_map.json` at `displayGraphList[*].graph.option.text`.
- Preserve graph-level parameter defaults, not just page-level parameters. Hidden graph parameters with non-empty defaults such as `openposition2`, `ad_space`, or `version` are upstream truth for downstream card reconstruction.
- When offline SQL is reused downstream for native-card exceptions, treat any `@param` placeholders as source-side syntax only. Before writing to KMB, convert them to Metabase template-tag form `{{param}}` and define matching `template-tags`.
- Keep `copyFrom` / `copyFromPage` only as supporting context. Do not treat a copy chain as proof that the current page has already been formally migrated.
- Preserve the full Space path and the raw graph identifiers even when the page itself is a pure container with no charts.
- If live page truth conflicts with an older local migration artifact, report the conflict and keep the live page metadata as the authoritative source.

## Output requirements

Return the identifiers needed downstream.

- `search`: page candidates with `page_id` and page name
- `page`: page metadata, graph inventory, complete page path, and any child-page identifiers needed for scoped descendant work
- `graph`: graph metadata, type, graph-level parameter defaults, and chart configuration needed to rebuild order or display intent
- `sql`: complete SQL text without truncating filters or parameter logic
- `tree`: navigable directory structure
- `text`: when a page contains `TEXT` graphs, preserve the raw text or HTML source needed to rebuild the dashboard note blocks downstream

For migration work, always preserve the full Space page `path` when it is available. That path is the default source for collection routing under `/kmb-migration`.

## Hand-off

- If the next step is modeling, hand off to `/kmb-sql-analyzer`.
- If the task is an end-to-end migration, hand off to `/kmb-migration` after extracting the needed page and graph context.

## Do not

- Do not design models, questions, or dashboards here.
- Do not treat a fuzzy search hit as a confirmed page selection.
