# Coohom Revenue Asset Catalog

Use this file to route Revenue asks to existing KMB assets. Start from the topic and collection, then narrow to dashboards and cards. Prefer reuse over rebuild.

Maintenance notes:
- Asset IDs and topic ownership can live here, but current parameter mappings, formulas, and chart behavior must be verified against live KMB before answering “latest” questions.
- If a preferred dashboard, card, or helper chain changes, update this file after confirming the live asset.
- Suggested metadata for volatile sections: `last_verified_at`, `verified_from`, `stability: likely-to-change`.
- If KMB exposes verification markers such as `moderated_status` or `moderation_reviews`, prefer marking those assets as the default reusable anchors.

## Collection Map

### Collection `114` - Revenue基础数据集

Role:
- Reusable Revenue datasets and standard questions for broader revenue semantics.

Pattern mix:
- Native datasets as base assets plus downstream MBQL and native presentation cards.
- Multiple dashboards with dimension-based parameter mappings.

Recommended reuse:
- Use this collection first for ARR, MRR, affiliate revenue, invoice-backed revenue logic, and reusable revenue questions.
- Reuse dashboard `161` for ARR and MRR explanations.
- Reuse dashboard `150` or card `2208` for channel or affiliate-related revenue slicing.

Pitfalls:
- This collection mixes base datasets and presentation cards; inspect the card purpose, not just the name.
- Do not route real-time “today/hourly” questions here first when `119` already covers them better.

Useful IDs:
- Datasets: `728`, `606`, `2205`, `2206`, `2211`, `2108`
- Cards: `2208`, `2209`, `2210`, `2114`, `2140`, `607`
- Dashboards: `161`, `150`, `156`, `109`

### Collection `119` - 实时-收入

Role:
- Real-time revenue monitoring for intra-day and day-over-day analysis.

Pattern mix:
- One native base dataset feeding many MBQL cards and real-time dashboards.
- Heavy reuse of card-backed sources for today, yesterday, hourly, and distribution views.

Recommended reuse:
- Use this collection first for today revenue, hourly revenue, yesterday comparison, and near-real-time distributions.
- Reuse dashboard `69` for the standard monitoring view.
- Use dashboard `98` when the user wants the AI-readout flavored version.

Pitfalls:
- Some cards are duplicates or temp variants; pick the stable dashboard-first entrypoint before choosing an individual card.
- This collection is not the best default for ARR, MRR, renewal, or LTV questions.

Useful IDs:
- Dataset: `3225`
- Cards: `631`, `639`, `640`, `641`, `642`, `643`, `644`, `645`, `648`, `651`, `652`, `6129`
- Dashboards: `69`, `98`

### Collection `116` - 续约/断约情况

Role:
- Renewal, churn, cancellation, and LTV-oriented analysis.

Pattern mix:
- Native model-like datasets feeding downstream dashboard analysis.
- Dashboard parameters stay dimension-based, but multiple lifecycle concepts coexist.

Recommended reuse:
- Use this collection first for renewal rate, churn, active cancellation, and LTV questions.
- Reuse dashboard `67` as the default lifecycle analysis entrypoint.
- Reuse dataset `1856` for invoice renewal logic and `1784` for active cancellation.

Pitfalls:
- Do not treat this as a general revenue trend collection.
- Renewal and churn questions often need business framing before raw numbers.

Useful IDs:
- Datasets: `1856`, `1784`
- Dashboard: `67`

### Collection `579` - TEAM数据（beta）

Metadata:
- `last_verified_at`: `2026-04-02`
- `verified_from`: `collection 579`, `dashboard 666`, `card 7807`, `card 8072`
- `stability`: `likely-to-change`
- `kmb_verified`: `false`

Role:
- TEAM upsell topic collection backing dashboard `666`.

Pattern mix:
- One invoice/detail helper plus one grouped helper for open-group logic.
- Dashboard `666` combines filters, time grouping, invoice/detail analysis on tab `468`, and open-group analysis on tab `469`.

Recommended reuse:
- Use this collection first for TEAM upsell amount, account counts, country distribution, purchase scene, and member level analysis.
- Start from dashboard `666`, then drop to the underlying cards only when the question is narrower.

Pitfalls:
- TEAM metrics are specialized; do not use them as a proxy for total Coohom revenue.
- Some cards answer similar questions with different groupings. Pick by dimension, not by similar title.

Useful IDs:
- Datasets: `7807`, `8072`
- Cards: `7765`, `7766`, `7767`, `7768`, `7769`, `7770`, `7771`, `7772`, `7773`, `7774`, `7797`, `8073`, `8074`, `8075`, `8076`, `8077`, `8078`
- Dashboard: `666`

## Dashboard Map

| Dashboard ID | Name | Collection | Topic | Core parameters | Recommended use |
|------|------|------|------|------|------|
| `161` | ARR&MRR | `114` | 基础收入 | date, string filters | Explain or inspect ARR and MRR |
| `150` | 收入金额按首次访问渠道分类数据 | `114` | 渠道收入 | date, channel-like dimensions | Revenue by first-visit channel |
| `156` | 25年收入分渠道 | `114` | 渠道收入 | limited filters | 2025 channel split snapshot |
| `109` | Coohom 收入趋势即席查询 | `114` | 基础收入 | country, SKU-like dimensions | Ad hoc trend exploration |
| `69` | 今日收入实时看板 | `119` | 实时收入 | multiple string filters | Standard real-time monitoring |
| `98` | 今日收入实时看板——加入AI解读 | `119` | 实时收入 | reduced filter set | Monitoring with AI-oriented narrative layer |
| `67` | LTV 与续约分析报表 | `116` | 续约断约 | string filters, date filters | Renewal, churn, and lifecycle value |
| `666` | TEAM 增购收入看板（728） | `579` | TEAM 增购 | `date`, `sku`, `member_level`, `purchase_scene`, `time_grouping` | Tab `468` for account/amount analysis, tab `469` for open-group analysis |

Metadata for dashboard `666`:
- `last_verified_at`: `2026-04-02`
- `verified_from`: `dashboard 666`
- `stability`: `likely-to-change`
- `kmb_verified`: `false`

## Core Card and Model Index

| Card ID | Name | Collection | Type | Upstream dependency | Main dimensions or metrics | Recommended use |
|------|------|------|------|------|------|------|
| `728` | dws_coohom_trd_daily_toc_invoice_s_d | `114` | dataset | native source | invoice-grain revenue detail | Base revenue source and reusable grain |
| `2206` | ods_payment_affiliate_s_d | `114` | dataset | native source | affiliate payment detail | Affiliate revenue base |
| `2208` | affiliate收入按周聚合 | `114` | query | `card__2206` | week, affiliate revenue | Weekly affiliate analysis |
| `2209` | MRR | `114` | native | native source | MRR trend | Standard MRR entrypoint |
| `2210` | ARR | `114` | native | native source | ARR trend | Standard ARR entrypoint |
| `607` | 到期应续续约率 | `114` | query | source-query based | renewal ratio | Reused renewal ratio logic |
| `1856` | invoice续约情况model | `116` | dataset | native source | renewal lifecycle fields | Base renewal model |
| `1784` | 主动取消订阅 | `116` | dataset | native source | churn and cancellation | Active cancellation analysis |
| `3225` | coohom账单表 | `119` | dataset | native source | real-time bill detail | Real-time monitoring base |
| `631` | 今日每小时收入 | `119` | query | `card__630`-style source chain | hour, revenue | Intra-day hourly trend |
| `639` | 今日收入 | `119` | query | `card__630`-style source chain | today revenue | Quick daily amount |
| `651` | 今日累计收入环比昨日 | `119` | query | `card__630`-style source chain | day-over-day revenue | Real-time comparison |
| `7765` | TEAM 增购 Helper Model（728） | `579` | query | `card__728` | SKU, member_level, purchase_scene, date | Core TEAM upsell reusable base |
| `7807` | TEAM Invoice Detail（728） | `579` | dataset | native source | invoice detail, country attribute, account amounts, account counts | TEAM invoice/detail base |
| `8072` | TEAM Group Fact（728） | `579` | dataset | `card__7807` | team group key, open_group_date, grouped account/amount fields | TEAM grouped open-group base |
| `7770` | TEAM 增购 按SKU聚合（728） | `579` | query | `card__7765` | SKU, amount, account counts | TEAM by SKU |
| `7771` | TEAM 增购 按member_level聚合（728） | `579` | query | `card__7765` | member_level, amount, account counts | TEAM by member level |
| `7772` | TEAM 增购 按购买场景聚合（728） | `579` | query | `card__7765` | purchase_scene, amount, account counts | TEAM by purchase scene |
| `7797` | TEAM 增购 金额（time-grouping） | `579` | query | `card__7765` | date, time grouping, amounts | TEAM time-series amount |
| `8073` | TEAM 账号数（time-grouping） | `579` | query | `card__7807` | date, time grouping, main/sub account counts | TEAM time-series account counts |
| `8074` | TEAM 开团数（time-grouping） | `579` | query | `card__8072` | open_group_date, time grouping, 开团数 | TEAM time-series open-group counts |
| `8075` | TEAM 开团国家 Top10 列表（Group Fact） | `579` | query | `card__8072` | country, 开团数 | Helper for open-group country bucketing |
| `8076` | TEAM 每日开团国家明细（Top10+其他，Group Fact） | `579` | query | `card__8072` + `card__8075` | open_group_date, country bucket, 开团数 | TEAM open-group country detail |
| `8077` | TEAM 每日开团数国家分布（Top10+其他，Group Fact） | `579` | query | `card__8072` + `card__8075` | open_group_date, country bucket, 开团数 | TEAM open-group country distribution trend |
| `8078` | TEAM 开团明细（Group Fact） | `579` | query | `card__8072` | open_group_date, team_group_order_id, grouped fields | TEAM open-group detail table |

## Key Dependency Chains

### ARR and MRR

- `114` -> dashboard `161`
- card `2209` answers MRR directly
- card `2210` answers ARR directly

### Affiliate Revenue

- dataset `2206` -> card `2208`
- dashboard `150` adds presentation and channel framing

### Renewal and LTV

- dataset `1856` + dataset `1784` -> dashboard `67`
- card `607` contributes reusable renewal-ratio logic

### TEAM Upsell

Metadata:
- `last_verified_at`: `2026-04-02`
- `verified_from`: `card 7807`, `card 8072`, `card 8073`, `card 8074`, `card 8075`, `card 8076`, `card 8077`, `card 8078`
- `stability`: `likely-to-change`
- `kmb_verified`: `false`

- dataset `728` -> card `7765`
- card `7765` -> `7766`, `7767`, `7768`, `7769`, `7770`, `7771`, `7772`, `7773`, `7774`, `7797`
- dataset `7807` -> `8072`, `8073`
- dataset `8072` -> `8074`, `8075`, `8076`, `8077`, `8078`
- dashboard `666` assembles the main TEAM upsell experience

## Dashboard `666` Parameters

| Parameter | Type | Purpose | Typical use |
|------|------|------|------|
| `date` | `date/all-options` | Revenue date filter | Time window selection |
| `sku` | `string/=` | Product or plan filter | Narrow by SKU |
| `member_level` | `string/=` | TEAM membership level | Compare level mix |
| `purchase_scene` | `string/=` | Purchase context | Compare upsell scenario |
| `time_grouping` | `temporal-unit` | day / week / month grain | Trend aggregation |

_Last updated: 2026-04-02_
