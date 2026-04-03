---
name: kmb-sql-analyzer
description: Analyze SQL for KMB migration. Use it after extracting source SQL to identify tables, dimensions, aggregations, and filters, then produce a migration plan for model, MBQL questions, and visualization.
---

# KMB SQL Analyzer

This is the required analysis step before building KMB resources.

## Inputs

Provide one of:

- `--sql-file <path>`
- `--sql "..."`

Optional:

- `--database <id>`
- `--output <path>`; default output is `migration_plan.json`

## Command

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/analyze_sql.py" --sql-file query.sql --output migration_plan.json
```

## What to verify

The resulting plan must make the core design choices explicit.

- Source tables and whether they are I tables or S tables
- Model granularity after removing aggregation
- Breakout alignment with original `GROUP BY`
- Aggregation naming aligned with the original SQL output names
- Whether conditional logic belongs in Model, MBQL, or Dashboard parameters
- Delivery decision fields:
  - `question_mode: mbql | native`
  - `shared_model_candidate`
  - `shared_question_base_candidate`
  - `dashboard_parameter_strategy: dimension | variable | mixed`

Use these decision defaults:

- Put wide-table joins, helper fields, and date standardization in the Model.
- Prefer MBQL when the chart can be expressed as `card__id` + breakout + aggregation + filter + joins + expressions.
- Mark `question_mode = native` when the source SQL depends on template tags, CTEs, window functions, funnel logic, or similarly SQL-native structures.
- Use `dashboard_parameter_strategy = dimension` for MBQL-first questions, `variable` for native questions driven by template tags, and upgrade to `mixed` at page level when one dashboard must coordinate both styles.

If needed, read shared guidance from `${CLAUDE_SKILL_DIR}/../kmb-metabase/references/mbql-best-practices.md` and `${CLAUDE_SKILL_DIR}/../kmb-metabase/references/rules/`.

## Output

Produce `migration_plan.json` with at least:

- `analysis`
- `delivery_decisions`
- `model`
- `questions`
- `visualization`

The output must be directly consumable by downstream skills:

- `model` -> `/kmb-model-builder`
- `questions[*]` -> `/kmb-question-builder`
- `visualization` -> `/kmb-viz-config`

If needed, align with `${CLAUDE_SKILL_DIR}/../kmb-metabase/references/skill-handoffs.md`.

## Hand-off

- Model creation: `/kmb-model-builder`
- Question creation: `/kmb-question-builder`
- Full orchestration: `/kmb-migration`

## Do not

- Do not skip this step during migration.
- Do not directly create Metabase assets here.

## Real patterns

- `collection 31` dashboard `63`: page-level parameter strategy is `mixed` because native template-tag cards and MBQL cards coexist.
- `collection 114` dashboard `161` and `collection 116` dashboard `67`: parameter mapping is primarily `dimension`.
