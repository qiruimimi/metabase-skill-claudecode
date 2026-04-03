---
name: kmb-collection-builder
description: Create, inspect, or update Metabase collections used by KMB workflows. Use it when the user needs a target collection prepared, but keep business-specific directory mapping in the workflow skill instead of here.
disable-model-invocation: true
---

# KMB Collection Builder

This skill provides atomic collection operations.

## Inputs

For create:

- `name`
- optional `parent_id`
- optional `description`

For update or inspection:

- `collection_id`

## Commands

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/create_collection.py" --name "【P56088】支付弹窗转化" --parent-id 565 --description "小站 page/56088 迁移" --skip-if-exists
```

## Rules

- Prefer idempotent creation with `--skip-if-exists` in migration work.
- Use naming like `【P<pageId>】<页面名>` for migration collections.
- For inspection work, remember that collection items marked as `dataset` are still read through `/api/card/{id}` in downstream APIs.
- Prefer `${CLAUDE_SKILL_DIR}/../kmb-metabase/scripts/inspect_collection.py` when you need a structural summary instead of a flat item list.
- When the collection hierarchy comes from Space migration context, let `/kmb-migration` decide the parent-child path and call this skill one level at a time.
- Return the resulting `collection_id`.
- Treat `collection_id` as the direct hand-off artifact for `/kmb-model-builder`, `/kmb-dashboard-builder`, or `/kmb-migration`.

## Do not

- Do not own business mapping from Space directory trees to collection hierarchies.
- Do not batch-create multi-level structures without surfacing each intermediate ID.

## Hand-off

- If collection strategy depends on migration context, hand off to `/kmb-migration`.
