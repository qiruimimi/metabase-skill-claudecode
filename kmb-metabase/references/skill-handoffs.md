# KMB Skill Handoffs

Use this file as the contract between KMB skills. The goal is to keep every hand-off explicit instead of relying on memory.

## Primary chain

`$kmb-space-query` -> `$kmb-sql-analyzer` -> `$kmb-model-builder` -> `$kmb-question-builder` -> `$kmb-viz-config` -> `$kmb-dashboard-builder`

Optional before the chain:

`$kmb-collection-builder`

Full orchestration:

`$kmb-migration`

## Contracts

### `$kmb-space-query`

- Produces: `page_id`, `graph_id`, page metadata, page `path`, raw SQL text, graph-level fixed parameter defaults, and `TEXT` HTML when present
- Hands off to:
  - `$kmb-sql-analyzer` when SQL is ready
  - `$kmb-migration` when the task is end-to-end

### `$kmb-sql-analyzer`

- Consumes: raw SQL from `$kmb-space-query` or user input
- Produces:
  - `migration_plan.json`
  - `model.sql` or equivalent model-ready SQL
  - `questions[]` config
  - `visualization` config
- Hands off to:
  - `$kmb-model-builder` with `migration_plan.json.model.sql`
  - `$kmb-question-builder` with `migration_plan.json.questions[*]`
  - `$kmb-migration` when the workflow stays centralized

### `$kmb-model-builder`

- Consumes:
  - `collection_id`
  - `model.sql` or `migration_plan.json`
- Produces:
  - `model_id`
- Hands off to:
  - `$kmb-question-builder` with `model_id`

### `$kmb-question-builder`

- Consumes:
  - `model_id`
  - one question config
  - `collection_id`
- Produces:
  - `question_id` or `card_id`
- Hands off to:
  - `$kmb-viz-config` with `card_id`
  - `$kmb-dashboard-builder` if styling is already done or not needed

### `$kmb-viz-config`

- Consumes:
  - `card_id`
  - visualization config
- Produces:
  - updated `card_id`
- Hands off to:
  - `$kmb-dashboard-builder`

### `$kmb-dashboard-builder`

- Consumes:
  - `collection_id`
  - dashboard name
  - ordered `card_id` list and layout config
- Produces:
  - `dashboard_id`

### `$kmb-collection-builder`

- Produces:
  - `collection_id`
- In migration context, may be called repeatedly to produce one `collection_id` per path level
- Hands off to:
  - `$kmb-model-builder`
  - `$kmb-dashboard-builder`
  - `$kmb-migration`

### `$kmb-migration`

- Owns the full chain
- Must keep the mapping:
  - `page_id -> graph_id -> sql -> model_id -> card_id -> dashboard_id`
- When no explicit KMB destination is provided for Space migration, must also keep:
  - `space_path -> resolved_collection_path_segments -> intermediate_collection_ids -> final_target_collection_id`
- For pages with graph-level defaults or `TEXT` blocks, must also keep:
  - `graph_id -> fixed_filters`
  - `text_graph_id -> rebuilt_text_artifact`

## Guardrails

- Do not jump directly from `$kmb-space-query` to `$kmb-model-builder`.
- Do not create Questions before `model_id` exists.
- Do not configure visualization before `card_id` exists.
- Do not assemble dashboards before card order and layout are explicit.
- For `_s_d` tables, let `$kmb-model-builder` enforce `ds_time` and `T+1 ds` rules.
- Do not let `$kmb-collection-builder` infer Space business hierarchy on its own; that routing decision belongs to `$kmb-migration`.
- Do not drop hidden graph parameter defaults during the `$kmb-space-query -> $kmb-sql-analyzer -> $kmb-migration` hand-off. They are part of the graph contract, not optional UI state.
