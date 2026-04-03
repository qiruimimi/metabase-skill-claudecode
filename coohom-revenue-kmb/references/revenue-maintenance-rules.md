# Coohom Revenue Maintenance Rules

Use this file to keep the Revenue skill aligned with changing KMB assets and metric logic. The main rule is simple: references help route and explain, but live KMB assets define the latest implemented truth.

## Truth Model

- `Live asset truth`: current dashboard, card, model, parameter mapping, and query definition in KMB
- `Reference truth`: stable business semantics, topic boundaries, default entrypoints, and known reusable asset anchors
- `KMB verification signal`: asset-side review markers such as `moderated_status` or `moderation_reviews` when they are actually populated

When they disagree:

- trust the live asset
- say that the reference looks stale
- update the reference after the answer or implementation task if appropriate

When KMB verification signals are absent:

- do not assume the asset is verified
- fall back to the normal live-first policy for changing logic

## What Must Be Verified Live

Always inspect current KMB assets before answering questions about:

- current metric logic or implemented formula
- current dashboard filters, parameters, defaults, and mappings
- current chart breakout, aggregation, or source chain
- current card fields, joins, expressions, or template tags
- whether a dashboard or card still exists and is still the preferred entrypoint

Even if an asset has a verification signal, still inspect it for exact “current/latest” implementation questions.

## What Can Be Answered From References First

You may answer from references first when the user is asking about:

- high-level topic boundaries
- stable business meaning
- which collection or dashboard usually owns a topic
- the default first place to look for a metric

If the user uses words like `现在`, `当前`, `最新`, `目前`, or asks for exact implemented logic, upgrade to live verification first.

## Using KMB Verification Signals

If KMB starts exposing reliable verification markers on Revenue assets:

- prefer those assets when choosing a default dashboard or card to reuse
- allow those assets to be summarized into references with higher confidence
- still live-check them for exact current logic when the user asks for the latest implementation

Use this priority:

1. verified KMB asset plus live inspection
2. unverified KMB asset plus live inspection
3. reference-only answer for stable semantic guidance

## Verification Triggers

Do a live KMB check before answering if any of these are true:

- the user asks for the current definition or latest口径
- the user asks how a current dashboard works
- the user asks what filters, dimensions, or formulas a current card uses
- the references mention a likely-to-change item such as dashboard parameters or helper-card dependencies
- there is any mismatch between remembered context and current asset metadata
- the candidate asset has no populated verification signal in KMB

## Suggested Verification Workflow

1. Use `revenue-domain-map.md` to identify the topic.
2. Use `revenue-asset-catalog.md` to locate the candidate dashboard, card, or model.
3. Use live KMB inspection through `$kmb-metabase` to confirm the actual current implementation.
4. Use `revenue-playbooks.md` to choose whether to answer, query deeper, or hand off to a builder skill.
5. If live and reference disagree, report the live version and mark the reference for update.

## Reference Update Rules

When a reference is updated, prefer lightweight metadata next to the changed section:

- `last_verified_at`: last date checked against live KMB
- `verified_from`: dashboard/card/model IDs used for verification
- `stability`: `stable` or `likely-to-change`

Use these defaults:

- business meaning and topic boundaries: `stable`
- dashboard parameter details: `likely-to-change`
- card dependency chains: `likely-to-change`
- collection-level topic ownership: `stable` unless the team is actively reorganizing assets

If a section is anchored to a KMB asset with a populated verification signal, add:

- `kmb_verified: true`
- `kmb_verification_source`: the asset ID carrying the signal

If no such signal exists, either omit the field or set:

- `kmb_verified: false`

## Section-Level Maintenance Hints

For `revenue-domain-map.md`:

- keep business definitions concise
- avoid hardcoding detailed formulas unless they are verified and stable
- add verification metadata only on terms whose implemented logic changes often

For `revenue-asset-catalog.md`:

- keep dashboard IDs, card IDs, parameter lists, and dependency chains close to live truth
- update this file whenever the preferred entrypoint changes
- mark dashboards and helper chains as `likely-to-change` when the team is iterating
- when KMB verification signals exist, note them near the relevant asset section

## TEAM Upsell Maintenance Lessons

Use these rules for TEAM upsell work in collection `579` and dashboard `666`.

- Separate `invoice grain` from `group grain` before changing any metric.
- Treat amount, `main_account_count`, and `sub_account_count` as invoice/detail metrics.
- Treat `open_group_count` as a grouped metric keyed by `team_group_order_id` or the business-approved group key.
- Do not answer or build a TEAM metric from name similarity alone when the grain is ambiguous.

### Modeling rule

- Keep one reusable invoice/detail Model for TEAM detail facts and helper attributes.
- Build a separate grouped Model for open-group logic when the metric is defined by group-level conditions.
- If the grouped Model can be derived from the invoice/detail Model, reference the existing saved card/model instead of duplicating the base SQL.

### Current implemented TEAM pattern

As of `2026-04-02`, the current live TEAM implementation follows this split:

- Invoice/detail base: card `7807` `TEAM Invoice Detail（728）`
- Group base: card `8072` `TEAM Group Fact（728）`

Current grouped open-group rule in card `8072`:

- `sum(sub_account_count) >= 1`
- or `sum(addon_quantity) >= 2`

Current grouped open-group outputs:

- `open_group_date`
- `team_group_order_id`
- `group_main_country`
- `total_addon_quantity`
- grouped account and amount fields

### Question and dashboard rule

- Keep account/amount Questions on the invoice/detail base.
- Keep open-group Questions on the grouped base.
- Do not put detail-grain account counts and group-grain open-group counts into one shared Question.
- In dashboard `666`, keep account/amount content on tab `468` and keep open-group content on tab `469`.

### Cleanup rule

- After replacing old TEAM open-group cards, archive the superseded cards rather than leaving two live definitions in the same collection.
- If a helper card is still used transitively by a live card, keep it and document the dependency instead of archiving it.

For `revenue-playbooks.md`:

- keep playbooks stable at the routing level
- do not hardcode fragile implementation details when a live check is more reliable
- if a playbook starts requiring too many exceptions, update the asset catalog first

## Answering Rule

When the user asks about the latest metric logic, answer in this pattern:

1. state the live asset checked
2. give the current implemented answer
3. mention if the skill reference agrees or appears stale

## Current Revenue Reality

As of `2026-04-02`, the checked Revenue assets in collections `114`, `119`, `116`, and `579` do not expose populated `moderated_status` values, and sampled dashboards/cards return empty `moderation_reviews`.

Practical effect:

- this skill should currently assume most Revenue assets are unverified at the KMB metadata layer
- for now, use verification signals only when they actually appear in future assets
- until then, keep the live-first fallback for changing logic

_Last updated: 2026-04-02_
