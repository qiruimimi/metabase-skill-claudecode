# Coohom Revenue Domain Map

Use this file to resolve business meaning before choosing a KMB asset. If one term can map to different scopes, explain the boundary first and then route to the best entrypoint.

Maintenance notes:
- This file is the semantic routing layer, not the final live implementation source for changing formulas.
- When the user asks for the latest implemented logic, verify the current KMB asset first.
- Suggested metadata for changed sections: `last_verified_at`, `verified_from`, `stability`.

## Topic Overview

| Topic | Core questions | Primary entrypoint | Notes |
|------|------|------|------|
| 基础收入 | ARR, MRR, 收入趋势, 渠道收入 | collection `114` | Reusable Revenue models and questions |
| 实时收入 | 今日收入, 每小时收入, 当日监控 | collection `119` | Real-time dashboard and monitoring questions |
| 续约断约 | 续约率, 断约, 主动取消订阅, LTV | collection `116` | Lifecycle and renewal analysis |
| TEAM 增购 | 增购金额, 主子账号, 开团, 购买场景 | dashboard `666`, collection `579` | Dedicated upsell topic with stable dashboard filters |

## Metric Glossary

### 收入

- 业务定义：广义收入话题，默认先指已支付收入而不是流量或注册行为。
- 主口径：优先用 Revenue 资产中的支付成功相关收入。
- 常见误解：实时收入、月经常性收入、续约收入都属于收入，但不是同一口径。
- 推荐入口：先分流到 `114`、`119`、`116` 或 `666` 对应主题。
- 相关维度：日期、国家、SKU、渠道、member_level、purchase_scene。

### ARR

- 业务定义：年经常性收入视角，用于观察长期订阅价值。
- 主口径：默认走 collection `114` 中的 ARR 现成卡片。
- 常见误解：不要把 ARR 和某一天或某周的收入趋势混用。
- 推荐入口：card `2210`, dashboard `161`。
- 适用场景：长期收入体量和订阅型收入观察。

### MRR

- 业务定义：月经常性收入视角，用于观察月度订阅收入变化。
- 主口径：默认走 collection `114` 中的 MRR 现成卡片。
- 常见误解：MRR 不是“本月总收入”的同义词。
- 推荐入口：card `2209`, dashboard `161`。
- 适用场景：订阅型收入趋势和月度稳定性分析。

### 新签收入

- 业务定义：首次付费或首次签约带来的收入。
- 主口径：优先从基础收入数据或实时收入卡片中拆分。
- 常见误解：不要和续约收入、升级收入混在一起。
- 推荐入口：先查 collection `114`，实时场景再看 `119`。
- 适用场景：新增付费增长、渠道质量评估。

### 续约收入

- 业务定义：来自续约账单或续订行为的收入。
- 主口径：和续约率、断约率一起看更有业务意义。
- 常见误解：续约收入高不等于续约率高。
- 推荐入口：collection `116`，必要时补 collection `114`。
- 适用场景：生命周期质量、老用户贡献分析。

### 代理收入

- 业务定义：来自代理相关账单或代理渠道的收入。
- 主口径：默认按现有 Revenue 基础资产解释。
- 常见误解：不要直接等同于 affiliate 收入，需按具体资产定义确认。
- 推荐入口：collection `114`, dashboard `150`, card `2208`。
- 适用场景：渠道贡献、结构占比分析。

### affiliate 收入

- 业务定义：affiliate 相关支付或分成视角的收入。
- 主口径：优先沿 `ods_payment_affiliate_s_d` 及其派生卡片解释。
- 常见误解：affiliate 不必然等于所有代理收入，需看实际口径。
- 推荐入口：dataset `2206`, card `2208`。
- 适用场景：按周或渠道聚合 affiliate 贡献。

### LTV

- 业务定义：生命周期价值，通常与续约、留存、断约放在一起分析。
- 主口径：默认走续约/断约专题资产。
- 常见误解：LTV 不是单次账单金额，也不是实时收入监控指标。
- 推荐入口：dashboard `67`, collection `116`。
- 适用场景：订阅生命周期、用户价值分层。

### 续约率

- 业务定义：到期后继续订阅的比例或相关比率口径。
- 主口径：优先复用已有续约分析卡片，不重新拼 SQL。
- 常见误解：需区分“应续再续”和泛化续约。
- 推荐入口：dashboard `67`, card `607`, dataset `1856`。
- 适用场景：订阅健康度分析。

### 断约

- 业务定义：未续订、失约或取消后流失的相关分析。
- 主口径：默认走续约/断约专题资产。
- 常见误解：主动取消订阅只是断约的一部分。
- 推荐入口：collection `116`, dataset `1784`, dashboard `67`。
- 适用场景：流失原因、断约结构拆分。

### 增购金额

- 业务定义：TEAM 增购专题中的新增购买金额，通常会区分主账号和子账号。
- 主口径：默认按 dashboard `666` 的专题资产解释。
- 常见误解：不要拿来替代全站总收入或实时收入。
- 推荐入口：dashboard `666`, card `7797`, card `7770`, card `7771`, card `7772`。
- 适用场景：TEAM upsell 专题分析。

### 开团数

Metadata:
- `last_verified_at`: `2026-04-02`
- `verified_from`: `dashboard 666`, `card 8072`, `card 8074`, `card 8077`, `card 8078`
- `stability`: `likely-to-change`
- `kmb_verified`: `false`

- 业务定义：TEAM 主题下按团级 key 统计的开团数量指标，不是 invoice 行数，也不是账号数。
- 主口径：优先沿当前 grouped Model 口径复用，不要在 invoice 粒度卡里临时拼 distinct 逻辑。
- 常见误解：开团数不是账号数，也不是支付订单数。
- 推荐入口：card `8074`, card `8077`, card `8078`, dashboard `666`。
- 适用场景：TEAM 增购行为活跃度、国家分布分析。

## Dimension Glossary

### 日期

- 定义：Revenue 问题的第一优先过滤维度。
- 常见过滤方式：日期区间、今天、昨日、过去 30 天、过去 3 个月。
- 高频主题：全部主题。
- 相关参数：`date`, dashboard date filters, `time_grouping`。

### 国家

- 定义：收入或行为的地域拆分维度。
- 常见过滤方式：单国家、Top 国家、国家分布。
- 高频主题：实时收入、TEAM 增购、渠道收入。
- 相关入口：collection `119`, collection `579`, dashboard `666`。

### SKU

- 定义：付费产品或套餐维度。
- 常见过滤方式：按 SKU 聚合或筛选。
- 高频主题：基础收入、实时收入、TEAM 增购。
- 相关参数：dashboard `666` 的 `sku`。

### member_level

- 定义：TEAM 主题下的会员层级维度。
- 常见过滤方式：筛选或按层级聚合。
- 高频主题：TEAM 增购。
- 相关参数：dashboard `666` 的 `member_level`。

### purchase_scene

- 定义：购买场景维度，用于区分 TEAM 增购发生的业务场景。
- 常见过滤方式：筛选或按场景聚合。
- 高频主题：TEAM 增购。
- 相关参数：dashboard `666` 的 `purchase_scene`。

### 时间粒度

- 定义：Revenue 趋势图的展示粒度。
- 常见值：`day`, `week`, `month`。
- 高频主题：TEAM 增购趋势图、基础收入趋势图。
- 相关参数：dashboard `666` 的 `time_grouping`。

## Topic Boundaries

### 基础收入 vs 实时收入

- 区别：基础收入关注稳定复用的数据集和标准分析；实时收入关注今天、昨日、小时级监控。
- 选型规则：问“今天怎么样”“按小时看”时先去 `119`；问“MRR/ARR/渠道收入”时先去 `114`。

### 收入分析 vs 续约分析

- 区别：收入分析看金额和结构；续约分析看生命周期、到期后是否继续订阅。
- 选型规则：只问收入规模时先走 `114` 或 `119`；问续约率、断约、LTV 时先走 `116`。

### 通用收入 vs TEAM 增购

- 区别：TEAM 增购是独立专题，口径、维度和仪表板参数都更专门化。
- 选型规则：只要问题包含 TEAM、member_level、purchase_scene、开团，就默认先看 `666`。

_Last updated: 2026-04-02_
