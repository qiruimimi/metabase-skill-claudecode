# Coohom Revenue Playbooks

Use these playbooks after the business topic is clear. Each playbook maps a common question style to the default Revenue assets, the minimum follow-up data needed, and the next KMB action.

Maintenance notes:
- Playbooks define routing and action order, not final live truth for changing asset logic.
- If a playbook points to a current dashboard, card, or parameter set, verify that live asset before answering “current” or “latest” questions.
- Update the linked asset references first when the preferred entrypoint changes.
- If a playbook conflicts with `SKILL.md` live-first rules, `SKILL.md` wins.

## General Rules

- First classify the ask as `metric_explain`, `asset_lookup`, `query_analysis`, or `build_or_extend`.
- Prefer dashboard-first routing for human questions and card-first routing for narrow analytical asks.
- Ask for the fewest missing filters possible.
- If an existing Revenue card already answers the question, reuse it instead of proposing new build work.

## PB-01 指标定义类

- 适用问法：`MRR 是什么` `ARR 和 MRR 区别` `LTV 是什么`
- 意图分类：`metric_explain`
- 先读：`revenue-domain-map.md`
- 默认入口资产：
  - ARR / MRR -> dashboard `161`, cards `2210` and `2209`
  - LTV / renewal -> dashboard `67`
- 需要补充的条件：通常不需要，除非用户要具体时段或维度。
- 回答时必须解释的业务点：指标含义、与相近指标的边界、推荐入口。
- 下一步动作：若用户继续要数据，再转对应 collection 或 dashboard。

## PB-02 基础收入分析类

- 适用问法：`最近收入趋势怎么看` `想看渠道收入` `看看 affiliate 收入`
- 意图分类：`asset_lookup` 或 `query_analysis`
- 先读：`revenue-domain-map.md`, `revenue-asset-catalog.md`
- 默认入口资产：
  - 通用收入 -> collection `114`
  - 渠道收入 -> dashboard `150` or `156`
  - affiliate -> dataset `2206`, card `2208`
- 需要补充的条件：日期范围、国家、渠道、SKU。
- 直接可复用的资产：dashboard `161`, `150`, `156`, `109`, card `2208`
- 下一步动作：用户要更细粒度图表时再考虑 `kmb-question-builder`。

## PB-03 实时收入监控类

- 适用问法：`今天收入怎么样` `按小时看今天收入` `昨天和今天比一下`
- 意图分类：`query_analysis`
- 先读：`revenue-domain-map.md`, `revenue-asset-catalog.md`
- 默认入口资产：collection `119`, dashboard `69`
- 需要补充的条件：是否要今天、昨日、小时级、国家、SKU。
- 直接可复用的资产：card `631`, `639`, `641`, `642`, `651`, dashboard `98`
- 回答时必须解释的业务点：这是实时监控视角，不是标准 MRR/ARR 口径。
- 下一步动作：若用户要定制新实时图，先确认现有卡片是否已经覆盖。

## PB-04 渠道 / 国家 / SKU 拆分类

- 适用问法：`收入按国家看` `按 SKU 看收入` `看不同渠道的收入分布`
- 意图分类：`query_analysis`
- 先读：`revenue-domain-map.md`, `revenue-asset-catalog.md`
- live check trigger:
  - if the user asks for the current implementation, current chart, latest parameter behavior, or current TEAM country/open-group chart, inspect the live card or dashboard before answering
- 默认入口资产：
  - 通用拆分 -> collection `114`
  - 当日或实时拆分 -> collection `119`
  - TEAM SKU 拆分 -> card `7770`
- 需要补充的条件：日期范围、要看的主题、是否是 TEAM。
- 直接可复用的资产：
  - dashboard `150`
  - TEAM SKU 拆分 -> card `7770`
  - TEAM 开团国家分布 -> card `8077`
- catalog discipline:
  - do not add a reusable card here unless it is also registered in `revenue-asset-catalog.md`
- 下一步动作：若不存在现成分组图，再转 `kmb-question-builder`。

## PB-05 续约 / 断约 / LTV 类

- 适用问法：`续约率怎么看` `断约情况在哪看` `LTV 用哪个报表`
- 意图分类：`metric_explain` 或 `asset_lookup`
- 先读：`revenue-domain-map.md`, `revenue-asset-catalog.md`
- 默认入口资产：collection `116`, dashboard `67`
- 需要补充的条件：日期范围、国家、SKU、是否只看主动取消订阅。
- 直接可复用的资产：dataset `1856`, dataset `1784`, card `607`
- 回答时必须解释的业务点：续约、断约、LTV 属于生命周期分析，不等于普通收入趋势。
- 下一步动作：如果用户要特定细分图表，再评估复用 `67` 里的现成卡片还是新建问题。

## PB-06 TEAM 增购专题类

- 适用问法：`TEAM 增购收入怎么看` `按 member_level 看 TEAM 增购` `按 purchase_scene 看 TEAM 金额`
- 意图分类：`query_analysis`
- 先读：`revenue-domain-map.md`, `revenue-asset-catalog.md`
- live check trigger:
  - if the user is asking how `666` currently works, what “开团数” currently means, which tab owns which chart, or which fields a current chart uses, inspect live dashboard `666` and the referenced cards first
- 默认入口资产：dashboard `666`
- 需要补充的条件：`date`, `sku`, `member_level`, `purchase_scene`, `time_grouping`
- 直接可复用的资产：
  - `7770` for SKU grouping
  - `7771` for member level grouping
  - `7772` for purchase scene grouping
  - `7797` for amount trend
  - `8073` for account counts trend
  - `8074` for open-group trend
  - `8076`, `8077` for open-group country detail and distribution
  - `8078` for open-group detail
- 回答时必须解释的业务点：TEAM 是独立专题，不代表全部 Revenue。
- 下一步动作：只有当现有卡片无法覆盖用户维度时，才转 `kmb-question-builder` and `kmb-viz-config`。

## PB-07 解释 Dashboard / Card 类

- 适用问法：`dashboard 666 这些筛选项什么意思` `这个 Revenue dashboard 里每张图是干嘛的`
- 意图分类：`asset_lookup` 或 `metric_explain`
- 先读：
  1. live dashboard/card
  2. `revenue-asset-catalog.md` only as a routing and naming aid
- 默认入口资产：指定 dashboard；若未指定则按主题选 `161`, `69`, `67`, or `666`
- 需要补充的条件：通常只需要 dashboard ID 或主题。
- 强制动作：
  - inspect the live dashboard payload before explaining parameters, tabs, defaults, or card ownership
  - inspect the live card payload before explaining breakout, aggregation, source chain, or field-level logic
- 直接可复用的资产：dashboard `161`, dashboard `69`, dashboard `67`, dashboard `666`
- 回答时必须解释的业务点：参数用途、默认分析主题、核心卡片分工。
- 下一步动作：用户要改 dashboard 时转 `kmb-dashboard-builder`。

## PB-08 新建图表 / 扩展 Dashboard 类

- 适用问法：`基于 Revenue 做一张新图` `给 666 加一个按国家的图` `做个 purchase_scene 趋势图`
- 意图分类：`build_or_extend`
- 先读：`revenue-asset-catalog.md`, then the topic-specific playbook above
- 默认入口资产：先找最接近的现成 card or dashboard
- 需要补充的条件：指标、维度、日期范围、目标 dashboard、是否允许新建 card
- 决策顺序：
  1. 找现成 dashboard
  2. 找现成 reusable card
  3. 找现成 base model or helper card
  4. 只有前面都不够时才新建
- Builder handoff:
  - Existing base is enough -> `$kmb-question-builder`
  - New chart style needed -> `$kmb-viz-config`
  - Need dashboard placement or parameter mapping -> `$kmb-dashboard-builder`
- 回答时必须解释的业务点：说明为什么复用已有资产或为什么必须新建。

## PB-09 资产定位类

- 适用问法：`Revenue 在 KMB 哪个 collection` `这个问题应该去哪个 dashboard 看`
- 意图分类：`asset_lookup`
- 先读：`revenue-domain-map.md`, `revenue-asset-catalog.md`
- 默认入口资产：
  - 基础收入 -> `114`
  - 实时收入 -> `119`
  - 续约断约 -> `116`
  - TEAM 增购 -> `666` / `579`
- 需要补充的条件：只在主题不清楚时补一个最小澄清。
- 下一步动作：如果用户确定了主题，再切到对应 playbook。

## Minimal Follow-up Rules

- 如果问题是指标定义，不追问过滤条件。
- 如果问题是“看哪里”，只在主题不清时补问一句。
- 如果问题是分析，优先补日期范围，其次补业务维度。
- 如果问题是 TEAM 专题，优先补 `date` 和 `time_grouping`，然后才是 `sku`, `member_level`, `purchase_scene`。
- 如果问题是建图，必须先确认现有 dashboard 或 card 是否已覆盖。

_Last updated: 2026-04-02_
