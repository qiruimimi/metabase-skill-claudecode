---
name: kmb-viz-config
description: Configure KMB card visualization settings such as chart type, metrics, dimensions, dual axes, percent formatting, and table behavior. Use it after question creation and before dashboard assembly.
disable-model-invocation: true
---

# KMB Visualization Config

Use this skill once a question or card already exists.

## Inputs

Required:

- `card_id`
- visualization config file or equivalent structured config

Optional:

- original graph type like `LineSimple`, `PieSimple`, or `MixLineBar`

## Command

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/update_viz.py" --card-id 6001 --config-file viz_config.json
```

## Guidance

- Map the original Space graph type to the closest KMB display.
- Use explicit `series_settings` and `column_settings` for dual-axis and percent fields.
- Do not use `display` alone to infer whether a card is MBQL or native. Real native cards may still render as `line`, `table`, or funnel-style views.
- Keep a small pattern library in mind:
  - `line`: trend or rate cards such as `collection 114` card `2208`
  - `combo`: mixed bar/line cards such as `collection 18` card `127`
  - `table`: detail or comparison cards such as `collection 116` card `607`
  - funnel/native special cases: `collection 31` cards `560/570`
- If the mapping is unclear, read `${CLAUDE_SKILL_DIR}/../kmb-metabase/references/dashboard-configs.md`.

## Output

Return the updated `card_id` and the effective visualization summary.

This updated `card_id` is the direct hand-off artifact for `/kmb-dashboard-builder`.

## Hand-off

- For page assembly, continue with `/kmb-dashboard-builder`.
