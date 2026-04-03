# Parameter Mapping Patterns

Read this when dashboard parameters need to connect to MBQL cards, native template-tag cards, or both.

## Dimension

Use this when a dashboard parameter maps directly onto a field or expression in a MBQL card.

Pattern:
- Target shape: `["dimension", ["field" | "expression", ...], {"stage-number": 0}]`
- Best fit for Model-backed or `card__id`-backed MBQL cards.

Examples:
- `collection 114` dashboard `161`
- `collection 116` dashboard `67`

Notes:
- One parameter can map to different fields on different cards.
- Temporal fields may use different grains per card; keep the explicit per-card target.

## Variable

Use this when a native question depends on Metabase template tags.

Pattern:
- Target shape: `["variable", ["template-tag", "<tag_name>"]]`

Examples:
- `collection 31` dashboard `63` mappings for native funnel cards such as `570`

Notes:
- Native cards with template tags usually need `variable` mapping even if the final display is a line or table.

## Mixed

Use this when one dashboard coordinates both MBQL cards and native template-tag cards.

Pattern:
- Same dashboard includes both `dimension` and `variable` mappings.

Examples:
- `collection 31` dashboard `63`

Notes:
- Decide this at page level, not by looking only at one card.
- Analyzer should mark `mixed` when the dashboard plan combines native exceptions with MBQL cards.

## Text Dashcard

Use this label for dashboard blocks where `card_id = null`.

Pattern:
- These are layout or explanatory blocks, not query cards.

Examples:
- `collection 18` dashboard `11`

Notes:
- Preserve them when updating dashboard layouts.
- Do not try to attach query parameter mappings to them.
