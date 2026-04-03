# Page 55839 Migration Checklist

Read this when you need a concrete, battle-tested runbook for a Space-to-KMB migration with shared SQL, repeated graphs, and dashboard filters.

## Standard sequence

1. Use `kmb-space-query` to inspect `page/55839`, enumerate displayed graph order, and extract the raw SQL for the unique source queries.
2. Use `kmb-sql-analyzer` to produce one `migration_plan.json` that records:
   - `query_id -> graph_id` reuse mapping
   - model grain
   - question breakout and aggregation plan
   - visualization type and dashboard order
3. Build one shared Model when the graphs differ only by breakout, aggregation, threshold, or display type.
4. Run `kmb-model-builder --validate-only` before creating the Model.
5. Create the Model and verify it with `/api/card/{id}/query`.
6. Create one KMB card per displayed Space graph, even when multiple graphs share one SQL or one MBQL shape.
7. Verify every created card with `/api/card/{id}/query`.
8. Apply visualization settings card by card.
9. Assemble the dashboard, then verify card order, card count, parameter existence, and parameter mappings.
10. Save runtime artifacts in the workspace: raw SQL, analyzer outputs, `migration_plan.json`, and `asset_mapping.json`.

## Problems hit in practice

- `POST /api/card` returned HTTP 400 for Questions when `display` and `visualization_settings` were missing.
- Assuming Tesseract MCP was available caused planning drift; the session needed an explicit fallback to offline `space-data/page_map.json`.
- Reused SQL made it tempting to reuse one card, but that breaks independent chart config and dashboard placement.
- Partial reruns left failed assets in the target collection and made IDs confusing until they were archived.

## Working defaults

- Put dynamic grain support such as `日/周/月` in the Model, not in repeated Question logic.
- Put threshold helpers such as `purchase_interval_days` in the Model so exploration stays in MBQL.
- Map dashboard date filters to a true date field like `signup_day_time`, not the display period field.
- Persist a `graph_id -> card_id -> dashboard_id` mapping file during the run instead of reconstructing it afterward.

## Quality gates

- Model SQL passes `_s_d` snapshot validation.
- Model query runs successfully.
- Every card query runs successfully.
- Dashboard card count and order match the source page.
- Dashboard parameters are present and mapped to the intended fields.
- Fallback sources and rerun decisions are recorded in `migration_plan.json`.
