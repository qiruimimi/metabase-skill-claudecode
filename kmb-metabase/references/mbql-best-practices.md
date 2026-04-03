# Metabase 最佳实践 (MBQL)

记录 KMB (Metabase) 使用中的经验总结和最佳实践。

---

## 0. 数仓表类型基础（重要前置知识）

### I表 vs S表

| 表类型 | 全称 | 特点 | Model 筛选策略 |
|--------|------|------|---------------|
| **I表** | 增量表 (Incremental) | 只记录变化数据 | **一般不筛选**，取全量 |
| **S表** | 快照表 (Snapshot) | 每天一个全量快照 | **必须筛选**，选某一天的快照 |

### S表筛选原则

```sql
-- ✅ 正确：选昨日快照（t+1）
WHERE ds = DATE_FORMAT(DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), '%Y%m%d')

-- ❌ 错误：不筛选会导致数据膨胀/重复
-- WHERE ds >= '20260101'  -- S表这样做会取到多天快照
```

### I表筛选原则

```sql
-- I表一般不筛选 ds（或根据需求筛选时间范围）
-- 但要注意 GROUP BY 时 I 表的 created/create/ds 是一致的
-- 可以用 Metabase API 先查一下：
-- SELECT * FROM {table_name} LIMIT 10
```

### 验证表类型和字段

```bash
# 用 Metabase API 查询表结构
curl -sL -X POST "${API_HOST}/api/dataset" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "database": 4,
    "native": {
      "query": "SELECT * FROM hive_prod.kdw_dw.dws_coohom_trd_daily_toc_invoice_s_d LIMIT 10"
    }
  }' | jq '.data[0]'
```

**需要确认**:
1. GROUP BY 字段（created_day）和 ds(ds_time) 是否一致
2. 时间字段是字符串类型还是 date 类型
3. 表是 I 表还是 S 表

---

## 1. MBQL 条件聚合（case 表达式）

### 核心语法：case 表达式结构

MBQL 的 `case` 表达式结构：

```
["case", [[condition, result]]]
     │      └── inner_case: 包含 [condition, result] 的数组
     └── case 关键字
```

### 单条件判断（无 AND）
```json
// ✅ 正确：is_proxy = 1 时求和 amt_usd
["sum", ["case", [[["=", ["field", "is_proxy", {"base-type": "type/Integer"}], 1], ["field", "amt_usd", {"base-type": "type/Float"}]]]]
```

### 多条件判断（带 AND）
```json
// ✅ 正确：is_proxy = 0 AND member_level = '新签' 时求和
["sum", ["case", [["and",
  ["=", ["field", "is_proxy", {"base-type": "type/Integer"}], 0],
  ["=", ["field", "member_level", {"base-type": "type/Text"}], "新签"]
], ["field", "amt_usd", {"base-type": "type/Float"}]]]]
```

**关键**: `[[condition, result]]` 中 condition 和 result 在同一个子数组里

### Python 生成器函数（推荐）

手动写 MBQL 容易括号错乱，**推荐用 Python 函数生成**：

```python
import json

def make_agg_with_and(name, filter_proxy, filter_level):
    """用于 is_proxy = X AND member_level = 'YYY' 的条件聚合"""
    cond1 = ["=", ["field", "is_proxy", {"base-type": "type/Integer"}], filter_proxy]
    cond2 = ["=", ["field", "member_level", {"base-type": "type/Text"}], filter_level]
    and_cond = ["and", cond1, cond2]
    result = ["field", "amt_usd", {"base-type": "type/Float"}]
    inner_case = [and_cond, result]  # 注意：不要额外括号！
    case_expr = ["case", [inner_case]]
    return ["aggregation-options", ["sum", case_expr], {"name": name, "display-name": name}]

def make_agg_simple(name, filter_proxy):
    """用于 is_proxy = X（无 AND）的简单条件聚合"""
    cond = ["=", ["field", "is_proxy", {"base-type": "type/Integer"}], filter_proxy]
    result = ["field", "amt_usd", {"base-type": "type/Float"}]
    inner_case = [cond, result]
    case_expr = ["case", [inner_case]]
    return ["aggregation-options", ["sum", case_expr], {"name": name, "display-name": name}]

# 使用示例
aggregation = [
    ["aggregation-options", ["sum", ["field", "amt_usd", {"base-type": "type/Float"}]], {"name": "周期总收入", "display-name": "周期总收入"}],
    make_agg_with_and("新签收入", 0, "新签"),
    make_agg_with_and("连续续约收入", 0, "连续续约"),
    make_agg_simple("代理收入", 1),
]
```

**关键点**: `case_expr = ["case", [inner_case]]` 而不是 `["case", [[inner_case]]]`

### ❌ 错误: 使用 `if` 表达式
```json
// 错误 - MBQL 不支持 if
["sum", ["expression", "if(category = 'A', amount, 0)"]]
```

### ❌ 错误: 括号结构不对
```json
// 错误 - 少了括号
["sum", ["case", [["=", ...], ["field", ...]]]]

// 错误 - 条件用了 AND 但结构不对
["sum", ["case", [["and", [...], [...]], ["field", ...]]]]
```

**原因**: MBQL 中条件判断使用 `case`，不是 `if`。`case` 语法更标准，支持多条件分支。

---

## 2. 字段类型：Integer vs Boolean

**重要发现**: 数据库 TINYINT 字段（如 `is_proxy`）在 Metabase 中映射为 `type/Integer`，**不是** `type/Boolean`。

### 错误做法
```json
// ❌ 错误 - 使用 boolean 比较
["=", ["field", "is_proxy", {"base-type": "type/Boolean"}], false]
["=", ["field", "is_proxy", {"base-type": "type/Boolean"}], true]
```

### 正确做法
```json
// ✅ 正确 - 使用 Integer 0/1 比较
["=", ["field", "is_proxy", {"base-type": "type/Integer"}], 0]
["=", ["field", "is_proxy", {"base-type": "type/Integer"}], 1]
```

**验证方法**: 查看 Model 6080 的字段定义确认实际 base-type。

---

## 3. 转化率计算

### ❌ 错误: 在 expressions 中定义转化率
```json
{
  "expressions": {
    "conversion_rate": ["/", ["field", 100], ["field", 101]]
  },
  "aggregation": [["sum", ["expression", "conversion_rate"]]]
}
```

### ✅ 正确: 在 aggregation 中直接计算
```json
{
  "aggregation": [
    ["/", ["sum", ["field", 100]], ["sum", ["field", 101]]]
  ]
}
```

**原因**:
- 转化率应该在聚合层面计算，避免行级别计算带来的精度问题
- 直接在 aggregation 中使用 `/` 运算，Metabase 会自动处理分母为0的情况

---

## 4. MBQL 与原生 SQL 的选择

> **前提**：本节讨论的是在 Model + MBQL 架构内部，Question 层应该用 MBQL 还是原生 SQL。API 端点与调用规范以 `rules/api-standards.md` 为准。

### 决策树

```
查询类型
├── 简单条件聚合（count/distinct/sum + case）→ MBQL ✅
├── Model 已有的字段组合 → MBQL ✅
├── `UNION ALL` / 多段逻辑 → 拆成多个 MBQL Question + Dashboard 组合 ✅
├── Model 没有的字段（如 order_type_user）→ 先在 Model 预加工补齐字段，再 MBQL ✅
├── 动态时间表达式 → 增量数据 + Dashboard 日期筛选 ✅
└── 复杂 JOIN / CTE / 窗口函数 → 先做 Model 分层拆解；仍无法落地再走原生 SQL 例外 ⚠️
```

### 迁移实战案例：page/55074 Revenue 用户分层（MBQL-first）

| 原 Graph ID | 推荐落地策略 | 说明 |
|------------|-------------|------|
| 6086 | MBQL | 简单聚合，字段在 Model 中可直接消费 |
| 6105 | MBQL | 简单聚合，字段在 Model 中可直接消费 |
| 72849 | 多 Question MBQL | 将 `UNION ALL` 逻辑拆成多张 Question，在 Dashboard 组合展示 |
| 72156 | Model 扩展 + MBQL | 先把 `order_type_user` 等字段在 Model 补齐，再做 MBQL |
| 72164 | Model 扩展 + MBQL | 同上 |
| 73163 | Model 分层 + MBQL | 先将 CTE 逻辑分层下沉到 Model，再做 MBQL |

**经验**: 当源 SQL 包含 Model 没有的字段时，先升级 Model；当出现 `UNION ALL` 时，优先拆成多个 MBQL Question。原生 SQL 仅作为最后手段，且必须记录“为什么拆不动、为什么补不全”。

---

## 5. Model 层与 Question 层的职责分工（核心原则）

> **铁律（针对 Model + MBQL 架构）**：Model 层负责预处理（字段转换、分类、别名等），Question 层负责简单消费（聚合、breakout、筛选）。

### 5.1 字段预处理 - 在 Model SQL 中完成

#### ✅ 正确做法（Model 层预处理）

```sql
-- Model SQL 示例
SELECT
  -- 1. CASE WHEN 提前计算分类字段
  CASE 
    WHEN channel IN ('google', 'facebook') THEN '付费渠道'
    WHEN channel IN ('organic', 'direct') THEN '自然渠道'
    ELSE '其他'
  END AS 频道,
  
  -- 2. 提前计算排序字段（用于 Question 层排序）
  CASE 
    WHEN channel IN ('google', 'facebook') THEN 1
    WHEN channel IN ('organic', 'direct') THEN 2
    ELSE 9
  END AS 频道排序,
  
  -- 3. 日期类型转换（避免 Question 层再转）
  STR_TO_DATE(ds, '%Y%m%d') AS 所在日,
  DATE_FORMAT(STR_TO_DATE(ds, '%Y%m%d'), '%Y-%m-%d') AS 所在日周,
  
  -- 4. 中文别名（Question 层直接用）
  uri AS 落地页,
  user_id,
  qhdi,
  reg_time
FROM source_table
```

#### ❌ 错误做法（在 Question 层用 MBQL 做 CASE WHEN）

```json
{
  "expressions": {
    "频道": ["case", [[["=", ["field", "channel", {}], "google"], "付费渠道"]]]
  }
}
```
**问题**：MBQL 的 `case` 语法复杂、容易出错，且每次查询都要重新计算。

### 5.2 Group By 对应关系

原 SQL 的 `GROUP BY` 必须和 Question 的 `breakout` **完全对应**：

| 原 SQL | Question MBQL |
|--------|---------------|
| `GROUP BY day, uri, ads_channel_classify` | `"breakout": ["所在日/周", "落地页", "频道"]` |

```json
{
  "breakout": [
    ["field", "所在日/周", {"base-type": "type/Text"}],
    ["field", "落地页", {"base-type": "type/Text"}],
    ["field", "频道", {"base-type": "type/Text"}]
  ]
}
```

### 5.3 聚合指标口径

| 指标 | 原 SQL | Question MBQL |
|------|--------|---------------|
| 全访客数 | `COUNT(DISTINCT a.qhdi)` | `["distinct", ["field", "qhdi", {}]]` |
| 全访客用户数 | `COUNT(DISTINCT b.qhdi)` | `["distinct", ["field", "有注册的qhdi", {}]]` |
| 当天总注册数 | `COUNT(DISTINCT IF(...))` | `["distinct", ["if", [[条件, ["field", "qhdi", {}]]]]]` |

**技巧**：用 `max(频道)` 和 `max(频道排序)` 在 GROUP BY 后取任意值：

```json
{
  "aggregation": [
    ["max", ["field", "频道", {"base-type": "type/Text"}]],
    ["max", ["field", "频道排序", {"base-type": "type/Integer"}]],
    ["distinct", ["field", "qhdi", {"base-type": "type/BigInteger"}]]
  ]
}
```

### 5.4 排序处理

#### ✅ 正确做法
在 **Model 层**用 `CASE WHEN` 计算排序字段（数字 1-8），Question 层直接按这个数字排序：

```json
{
  "order-by": [
    ["asc", ["field", "频道排序", {"base-type": "type/Integer"}]]
  ]
}
```

#### ❌ 错误做法
在 Question 层用 MBQL 表达式做 `CASE WHEN` 排序 —— 太麻烦且容易出错。

### 5.5 对照表：Model 层 vs Question 层

| 步骤 | Model 层（SQL） | Question 层（MBQL） |
|------|----------------|-------------------|
| **字段预处理** | CASE WHEN 计算分类、排序字段 | 直接用预计算好的字段 |
| **日期转换** | `STR_TO_DATE(ds, '%Y%m%d')` → `ds_time` | 直接用 `ds_time` |
| **别名** | SQL 中用中文别名 | 直接用中文别名引用 |
| **Group By** | SQL 中 `GROUP BY` | `breakout` 必须和 SQL 一致 |
| **Aggregation** | SQL 中聚合 | `max(分组字段)` + `distinct(指标)` |
| **Order By** | 预计算排序字段 | 直接用数字字段排序 |

### 5.6 时间字段处理（补充）

#### 时间字段类型转换

**重要**: 数仓中时间字段通常是字符串格式（如 `%Y%m%d`），需要转换为 date 类型用于 Question 层。

```sql
-- Model SQL 中做时间类型转换
SELECT
  ds,                                          -- 字符串，如 '20260324'
  STR_TO_DATE(ds, '%Y%m%d') AS ds_time,        -- 转换为 date 类型
  DATE_FORMAT(STR_TO_DATE(ds, '%Y%m%d'), '%Y-%u') AS week_start,  -- 周
  DATE_FORMAT(STR_TO_DATE(ds, '%Y%m%d'), '%Y-%m') AS month_start  -- 月
FROM table
```

#### Question 层使用原则

| 场景 | 推荐字段 | 原因 |
|------|---------|------|
| **Breakout/横坐标** | `ds_time` (date 类型) | 按天/周/月聚合时，date 类型更准确 |
| **Group By** | 与 ds 一致的字段 | 如果 created_day = ds，则用 ds_time |
| **筛选器** | date 类型字段 | Dashboard 筛选器需要 date 类型 |

```json
// ✅ 正确：使用 date 类型字段做 breakout
{
  "breakout": [
    ["field", "ds_time", {"base-type": "type/Date"}]
  ]
}

// ❌ 错误：使用字符串类型做 breakout（可能导致排序问题）
{
  "breakout": [
    ["field", "pay_success_day", {"base-type": "type/Text"}]
  ]
}
```

#### I 表特殊处理

对于 I 表（增量表），created/create/ds 一般一致，此时：
- 直接用 `ds_time` 做 Group By
- 不需要额外的时间转换逻辑

```sql
-- I 表示例
SELECT
  ds,
  STR_TO_DATE(ds, '%Y%m%d') AS ds_time,
  user_id,
  amt_usd
FROM hive_prod.kdw_dw.dws_coohom_trd_daily_toc_invoice_i_d
-- 不筛选 ds，因为 I 表记录增量
```

**原因**:
- Model 层预处理保证计算逻辑统一
- 避免每个 Question 重复定义时间转换逻辑
- 查询性能更好
- 减少 MBQL 复杂度和出错概率
- **Dashboard 筛选器需要 date 类型字段才能正确关联**

### ⚠️ Dashboard 筛选器关联失败的根本原因

**问题**: 如果 Question 使用字符串类型时间字段（如 `pay_success_day`），Dashboard 筛选器无法关联。

**解决**: Model 层必须提供 date 类型时间字段：

```sql
-- ✅ Model 中提供 date 类型字段
SELECT
  ds,
  STR_TO_DATE(ds, '%Y%m%d') AS ds_time,  -- date 类型
  pay_success_day,
  STR_TO_DATE(pay_success_day, '%Y%m%d') AS pay_success_time,  -- date 类型
  ...
FROM table
```

**Question breakout 使用 ds_time 而非 pay_success_day**:
```json
// ✅ 正确：breakout 使用 date 类型
"breakout": [["field", "pay_success_time", {"base-type": "type/Date"}]]

// ❌ 错误：breakout 使用字符串类型
"breakout": [["field", "pay_success_day", {"base-type": "type/Text"}]]
```

**后果**: 使用字符串类型字段会导致 Dashboard 参数筛选无法工作！

---

## 6. 可视化设计

### 参考 Dashboard 700 的设计原则

#### 精简指标展示
- 只展示 3-5 个核心指标
- 使用 **统计数字卡片 (Scalar)** 突出关键数据
- 避免信息过载

#### 双 Y 轴设计
```json
{
  "visualization_settings": {
    "graph.y_axis.title_text": "金额",
    "graph.y_axis.max": null,
    "graph.y_axis.min": null,
    "graph.series_settings": {
      "series_1": {
        "axis": "left"    // 金额类指标 - 左轴
      },
      "series_2": {
        "axis": "right"   // 比率类指标 - 右轴
      }
    }
  }
}
```

**应用场景**:
- 左轴: 金额类指标（花费、收入）
- 右轴: 比率类指标（转化率、ROAS）

#### 面积图 (Area Chart) 使用
- 用于展示**累积趋势**或**占比变化**
- 适合展示随时间变化的整体构成
- 设置 `stackable.stack_type: "stacked"` 实现堆叠效果

```json
{
  "display": "area",
  "visualization_settings": {
    "stackable.stack_type": "stacked",
    "graph.dimensions": ["date"],
    "graph.metrics": ["metric_1", "metric_2", "metric_3"]
  }
}
```

---

## 7. Question 设计模式

### 标准结构
```json
{
  "name": "指标名称",
  "dataset_query": {
    "database": 4,
    "type": "query",
    "query": {
      "source-table": 123,
      "aggregation": [
        ["sum", ["field", 456]],
        ["/", ["sum", ["field", 789]], ["sum", ["field", 101]]]
      ],
      "breakout": [
        ["field", 201, {"temporal-unit": "week"}]
      ],
      "filter": [
        "and",
        ["time-interval", ["field", 200], -30, "day"]
      ]
    }
  },
  "display": "line",
  "visualization_settings": {
    "graph.dimensions": ["date"],
    "graph.metrics": ["sum"]
  }
}
```

---

## 8. 性能优化建议

1. **使用 Model 作为数据源**
   - 避免直接从大表查询
   - Model 可以预聚合、预过滤

2. **合理使用 Filter**
   - 添加时间范围过滤减少数据量
   - 使用索引字段进行过滤

3. **限制返回行数**
   - 可视化图表不需要太多数据点
   - 使用 `limit` 控制返回行数

4. **避免嵌套过深的表达式**
   - 复杂的计算在 Model 层或数据库层完成

---

## 9. 调试技巧

### 查看生成的 SQL
在 Metabase 界面:
1. 打开 Question
2. 点击右上角的 "..."
3. 选择 "View the SQL"

### 使用 API 验证
```bash
# 获取 Question 配置
curl -H "x-api-key: $API_KEY" \
  "https://kmb.qunhequnhe.com/api/card/4953"

# 执行查询
curl -X POST \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  "https://kmb.qunhequnhe.com/api/card/4953/query"
```

---

## 10. Dashboard 筛选器配置

### 创建带筛选器的 Dashboard

```bash
curl -X PUT "${HOST}/api/dashboard/${dashboard_id}" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": [
      {
        "name": "日期范围",
        "slug": "date_range",
        "id": "param_date",
        "type": "date/range"
      }
    ],
    "dashcards": [
      {
        "id": -1,
        "card_id": 6092,
        "row": 0,
        "col": 0,
        "size_x": 18,
        "size_y": 8
      },
      {
        "id": -2,
        "card_id": 6105,
        "row": 8,
        "col": 0,
        "size_x": 18,
        "size_y": 8
      }
    ]
  }'
```

### 筛选器类型

| 类型 | slug 示例 | 说明 |
|------|----------|------|
| `date/range` | `date_range` | 日期范围筛选 |
| `date/relative` | `date_relative` | 相对日期（如最近30天） |
| `location/city` | `city` | 城市筛选 |
| `location/state` | `state` | 州/省筛选 |
| `location/zip_code` | `zip` | 邮编筛选 |
| `id` | `user_id` | ID 筛选 |
| `category` | `category` | 分类筛选 |
| `enum/...` | `enum_xxx` | 枚举筛选 |

### 布局参数

| 参数 | 说明 | 建议值 |
|------|------|-------|
| `size_x` | 宽度 | 全宽 18，半宽 9 |
| `size_y` | 高度 | 数字卡片 4，图表 6-8，表格 8-12 |
| `row` | 行位置 | 从 0 开始 |
| `col` | 列位置 | 从 0 开始 |
| `id` | 卡片 ID | 新卡片用负数 (-1, -2...) |

**注意**: `PUT /api/dashboard/:id` 会**替换**整个 Dashboard 配置，包括已有的 Cards。

---

*最后更新: 2026-03-25*
