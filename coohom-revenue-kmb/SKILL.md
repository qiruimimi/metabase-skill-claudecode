---
name: coohom-revenue-kmb
description: Revenue domain skill for Coohom on KMB. Use it when the user asks where to find Coohom Revenue data, wants revenue metric definitions, needs natural language routed to the right collection/dashboard/card, or wants to query or extend existing Revenue assets in KMB.
---

# Coohom Revenue KMB

Use this skill as the domain entrypoint for Coohom Revenue work on KMB. This skill owns revenue semantics, asset routing, and action playbooks. It does not replace the generic `kmb-*` builder skills.

## When to use

- The user asks about Coohom Revenue, ARR, MRR, revenue trend, affiliate revenue, renewal, churn, LTV, or TEAM upsell revenue.
- The user wants to know which KMB collection, dashboard, card, or model should answer a Revenue question.
- The user asks for natural-language analysis on top of existing Revenue assets.
- The user wants to extend an existing Revenue dashboard or create a new chart from known Revenue data.

## First-pass coverage

First read this skill as covering the core Revenue entrypoints below.

- Collection `114`: `Revenue基础数据集`
- Collection `119`: `实时-收入`
- Collection `116`: `续约/断约情况`
- Dashboard `666`: `TEAM 增购收入看板（728）`
- Collection `579`: `TEAM数据（beta）` supporting dashboard `666`

If the answer is not in these entrypoints, fall back to shared KMB search or upstream Space discovery.

## Intent classes

Classify each request into one of these buckets before answering.

- `metric_explain`: explain business meaning, scope, and metric boundaries
- `asset_lookup`: identify the right collection, dashboard, card, or model
- `query_analysis`: use existing Revenue assets to answer or structure analysis
- `build_or_extend`: create or extend a question, chart, or dashboard only after confirming reuse is insufficient

## Workflow

1. Read `references/revenue-domain-map.md` first to resolve business semantics.
2. Read `references/revenue-asset-catalog.md` to map the ask to existing collections, dashboards, cards, and dependencies.
3. Read `references/revenue-playbooks.md` only for the matching user pattern.
4. Before answering any current metric definition, field mapping, dashboard parameter, card logic, or chart behavior question, verify the live KMB asset first.
5. Prefer reusing an existing Revenue asset before suggesting new build work.
6. If the user explicitly wants a new or changed Metabase asset, hand off to the right `kmb-*` skill.

## Routing

- Shared KMB search, collection inspection, and direct card queries: use `/kmb-metabase`
- Upstream Space discovery when KMB Revenue assets are insufficient: use `/kmb-space-query`
- Create or update a KMB collection: use `/kmb-collection-builder`
- Create MBQL questions from an existing model or card-backed base: use `/kmb-question-builder`
- Configure chart visuals: use `/kmb-viz-config`
- Build or update dashboards: use `/kmb-dashboard-builder`

## Output contract

Return concise, structured answers with these parts whenever relevant:

- `业务解释`: what the metric or topic means
- `推荐资产入口`: the best collection, dashboard, card, or model and its ID
- `推荐查询方式`: which filters or dimensions matter
- `下一步动作`: answer directly, query an existing asset, or hand off to a builder skill

## Source priority

For Revenue questions, use this order of truth:

1. Live KMB assets and `kmb-metabase` helpers for anything that can change, including current metric logic, filter behavior, parameter mappings, and chart configuration
2. This skill's Revenue references for semantic routing, stable domain context, and default entrypoints
3. Upstream Space data only when current Revenue KMB assets do not cover the ask

## Live verification rules

Treat the references in this skill as routing and semantic aids, not as the final source of truth for changing definitions.

- If a referenced dashboard or card has a usable KMB verification signal such as non-empty `moderated_status` or non-empty `moderation_reviews`, you may treat the asset as more trustworthy for routine semantic routing and lower the need for repeated deep checks.
- If those verification signals are absent, default to live-first for current implementation questions.
- If the user asks what the current metric definition is, inspect the current dashboard, card, or model before answering.
- If the user asks how a dashboard currently filters or groups data, inspect the live dashboard and its parameter mappings before answering.
- If the user asks what fields a chart uses or where a number comes from, inspect the live card or model before answering.
- If the current live asset conflicts with a reference in this skill, trust the live asset and explicitly say that the reference appears stale.
- When the live asset confirms the reference, answer normally without repeating the full verification process.

## Practical rules

- Explain semantic differences before routing if a term can map to multiple metrics or time windows.
- Do not default to creating a new card when an existing dashboard or card already answers the question.
- Treat dashboard `666` as the default TEAM upsell entrypoint, especially for `date`, `sku`, `member_level`, `purchase_scene`, and `time_grouping`.
- Treat collection `119` as the default entrypoint for real-time and intra-day revenue monitoring.
- Treat collection `114` as the default entrypoint for reusable Revenue base assets and broader revenue semantics.
- Treat collection `116` as the default entrypoint for renewal, churn, and LTV-style analysis.
- For static business definitions such as topic boundaries, use the references directly unless the user is explicitly asking for the latest implemented logic.
- Prefer assets with explicit KMB verification metadata when multiple candidate dashboards or cards answer a similar Revenue question.

## Do not

- Do not redefine generic KMB API or Metabase builder rules here.
- Do not duplicate large card inventories in the skill body; keep them in references.
- Do not jump into build work before checking reusable Revenue assets.
- Do not answer a Revenue question from vague name similarity alone; use the mapped assets and business topic.
- Do not answer a “current” or “latest” metric question from references alone when a live KMB asset can be inspected.

## References

- Revenue semantics: `references/revenue-domain-map.md`
- Revenue asset map: `references/revenue-asset-catalog.md`
- Revenue action playbooks: `references/revenue-playbooks.md`
- Revenue maintenance rules: `references/revenue-maintenance-rules.md`
