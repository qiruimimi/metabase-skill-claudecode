# Collection Patterns

Real patterns learned from established KMB collections. Read this when you need grounded examples for Model boundaries, MBQL reuse, native-question exceptions, or dashboard assembly.

## Collection 18: Coohom 访客

Role:
- Visitor analytics with one shared base question feeding multiple presentation cards and large dashboards.

Pattern mix:
- MBQL-heavy card layer on top of shared `card__...` bases.
- Dashboards can be large and may contain text blocks with `card_id = null`.

Recommended reuse:
- Reuse one stable visitor base card or model, then split final charts into separate cards.
- Good examples: `124` and `127` both derive from `card__121`, but stay independent because breakout and chart behavior differ.

Pitfalls:
- Do not collapse multiple presentation charts into one card just because they share the same source.
- Large dashboards may have sparse or missing parameter mappings on informational blocks.

Useful IDs:
- Cards: `124`, `127`
- Dashboard: `11`

## Collection 114: Revenue基础数据集

Role:
- Revenue-facing reusable datasets plus MBQL questions and dashboards with regular dimension mappings.

Pattern mix:
- Shared dataset/model layer, then MBQL cards on top.
- Dashboard parameters mostly map through `dimension` targets.

Recommended reuse:
- Keep invoice- or revenue-grain detail in the Model.
- Build downstream MBQL cards for weekly, monthly, country, and SKU slices.
- Good example: `2208` uses `joins` and weekly breakout on top of a reusable card-backed dataset.

Pitfalls:
- Cards listed as `dataset` in collection items are still card-backed assets.
- Display type such as `line` does not imply the asset is native or MBQL; inspect `dataset_query.type`.

Useful IDs:
- Cards: `2208`, `728`
- Dashboards: `161`, `156`

## Collection 116: 续约/断约情况

Role:
- Renewal analytics where one wide invoice model supports downstream derived questions and dashboards.

Pattern mix:
- Reusable native model-like datasets, then MBQL cards with `source-query` and expressions.
- Dashboard mappings remain mostly `dimension` based, but multiple time fields can coexist.

Recommended reuse:
- Put invoice lifecycle fields and renewal helper attributes in the base Model.
- Use MBQL `source-query` and expressions for ratio and comparison charts.
- Good example: dashboard `67` reuses card `607` from `collection 114` rather than re-implementing the ratio logic as a new native card.

Pitfalls:
- One dashboard parameter may point to different date fields on different cards.
- Do not force a single global date field when the source cards are intentionally different.

Useful IDs:
- Cards: `1856`, `1784`
- Dashboard: `67`

## Collection 31: 模型数据

Role:
- Mixed model funnel analytics with both reusable datasets and native template-tag driven cards.

Pattern mix:
- Native cards remain common for funnel logic and template-tag driven exploration.
- Dashboards may mix `dimension` mappings for MBQL cards with `variable` mappings for native cards.

Recommended reuse:
- Keep reusable model behavior data in datasets or Models.
- Preserve native questions when the chart depends on template tags, funnel logic, or complex SQL.
- Good examples: `560` and `570` are native, but still participate in dashboards alongside MBQL cards.

Pitfalls:
- Do not classify cards by `display` alone; `line` can still be native.
- Expect mixed dashboard parameter strategy when native and MBQL cards coexist.

Useful IDs:
- Cards: `560`, `570`, `794`
- Dashboards: `63`, `22`
