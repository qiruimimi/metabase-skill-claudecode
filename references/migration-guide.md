# 小站到 KMB 迁移完整流程

> 来源: 书航提供的实战流程 (2026-03-18)

## 🔄 总体流程

```
阶段1: 分析原配置 → 阶段2: 创建Model → 阶段3: 创建Question(MBQL) 
→ 阶段4: 配置可视化 → 阶段5: 创建Dashboard → 阶段6: 数据验证
```

---

## 阶段1：分析原配置

### 1.1 获取并分析原SQL

```bash
# 从 space_sql_mapper 获取 SQL
python3 scripts/space_sql_mapper.py graph <graphId>
```

**分析 checklist:**
- [ ] **SELECT 字段** → 确定 aggregation 指标
- [ ] **GROUP BY 字段** → 确定 breakout 维度
- [ ] **WHERE 条件** → 确定 filter 逻辑
- [ ] **时间粒度** (日/周/月) → 确定 temporal-unit

### 1.2 获取前端配置

从 `page_map.json` 的 `displayGraphList` 中获取:

| 配置项 | 含义 | 对应 KMB |
|--------|------|----------|
| `graphType` | 图表类型 | `display` |
| `legendFilterList` | 显示哪些指标 | `graph.metrics` |
| `yAxisIndex` | 单轴/双轴 | `series_settings[].axis` |
| `xKey` | X轴字段 | `graph.dimensions` |
| `yKey` | Y轴字段 | `graph.metrics` |
| `groupKey` | 分组字段 | breakout 第二个字段 |

**图表类型映射:**
| 原 graphType | KMB display | 说明 |
|--------------|-------------|------|
| LineSimple | `line` | 简单线图 |
| BarNegative | `bar` | 柱状图，可能需要调整维度顺序 |
| PieSimple | `pie` | 饼图，需配置 `pie.dimension` |
| MixLineBar | - | 部分 line + 部分 bar + 双Y轴 |

---

## 阶段2：创建Model

**目的**: 提供干净、可复用的数据层

### 步骤

1. **从原SQL提取基础字段** (移除聚合，保留原始粒度)
2. **预处理字段** (如 `str_to_date`, `date_format`)
3. **添加计算字段** (如 `coalesce` 处理 NULL)
4. **注意**: Model 不做 ds 筛选，保留全量数据

### API

```bash
POST /api/card
{
  "type": "model",
  "name": "Model: {业务名}",
  "collection_id": {target_collection},
  "display": "table",              // ✅ 必需字段
  "visualization_settings": {},    // ✅ 必需字段（可为空）
  "dataset_query": {
    "type": "native",
    "native": {
      "query": "SELECT 基础字段 FROM 表 WHERE 条件(不做ds筛选)",
      "template-tags": {}
    },
    "database": {database_id}
  }
}
```

**注意**: `display` 和 `visualization_settings` 是必需字段，否则 API 会返回错误。

### Model SQL 示例

```sql
-- 原SQL (聚合后)
SELECT 
  pay_success_day,
  COUNT(DISTINCT user_id) as dau
FROM table
WHERE ds = '20260301'
GROUP BY pay_success_day

-- Model SQL (原始粒度)
SELECT 
  pay_success_day,
  user_id,
  -- 预处理字段
  date_format(event_time, '%Y%m%d') as event_day
FROM table
-- 注意: 不做 ds 筛选，保留全量
```

---

## 阶段3：创建 Question (MBQL)

**核心原则**:
- `aggregation`: **建全**所有需要的指标 (如9个)
- `breakout`: **严格按**原SQL的 GROUP BY 配置

### 步骤

1. **配置 source-table**: `"card__{model_id}"`
2. **配置 breakout**: 维度字段 (时间/渠道/国家等)
3. **配置 aggregation**:

```json
// 普通聚合
["distinct", ["field", "user_id"]]

// 条件聚合 (case 不是 if)
["distinct", 
  ["case", [
    [["=", ["field", "order_type"], "New"], ["field", "user_id"]]
  ]]
]

// 转化率 (直接计算)
["/", 
  ["distinct", ["field", "registered_users"]], 
  ["distinct", ["field", "visited_users"]]
]
```

4. **保持原SQL名称**: aggregation-options 的 name 与原SQL列名一致

### API

```bash
POST /api/card
{
  "type": "question",
  "name": "{原图表名}",
  "collection_id": {target_collection},
  "dataset_query": {
    "type": "query",
    "database": {database_id},
    "query": {
      "source-table": "card__{model_id}",
      "breakout": [
        ["field", "date_field", {"temporal-unit": "day"}],
        ["field", "dimension_field"]
      ],
      "aggregation": [
        ["aggregation-options", ["distinct", ["field", "user_id"]], {"name": "用户数"}]
      ]
    }
  }
}
```

---

## 阶段4：配置可视化

**核心原则**:
- `graph.metrics`: **只显示**前端需要的指标 (如2个)
- `display`: 匹配原 `graphType`
- `series_settings`: 配置每个指标的显示方式

### 配置映射

| 原 graphType | KMB 配置 |
|--------------|----------|
| LineSimple | `display: "line"` |
| BarNegative | `display: "bar"` + 调整 dimensions 顺序 |
| PieSimple | `display: "pie"` + `pie.dimension` 配置 |
| MixLineBar | 部分 line + 部分 bar + 双Y轴 |

### 通用设置

```json
{
  "display": "line",
  "graph.dimensions": ["日期"],
  "graph.metrics": ["显示指标1", "显示指标2"],
  "graph.show_values": true,
  "series_settings": {
    "访客数": {"axis": "left", "display": "area"},
    "注册率": {"axis": "right", "display": "line"}
  },
  "column_settings": {
    "[\"name\",\"注册转化率\"]": {"number_style": "percent"}
  }
}
```

### API

```bash
# 获取当前配置
GET /api/card/{id}

# 更新可视化配置
PUT /api/card/{id}
{
  "visualization_settings": {...}
}
```

---

## 阶段5：创建 Dashboard

### 步骤

0. **（可选）创建子 Collection** ⭐

为了保持资源整洁，建议为每个迁移的页面创建独立的子 Collection：

```bash
POST /api/collection
{
  "name": "【{pageId}】{页面名}",
  "description": "小站 page/{pageId} 迁移版本",
  "parent_id": {parent_collection_id}  // 如 485 (Traffic)
}
```

**推荐命名规范**: `【55074】Revenue用户分层`

1. **创建 Dashboard**

```bash
POST /api/dashboard
{
  "name": "{Dashboard名}",
  "collection_id": {target_collection},
  "parameters": [
    {
      "name": "日期范围",
      "slug": "date_range",
      "id": "param1",
      "type": "date/all-options"
    }
  ]
}
```

2. **添加卡片**

```bash
PUT /api/dashboard/{dashboard_id}
{
  "dashcards": [
    {
      "id": -1,  // 负数id
      "card_id": {question_id},
      "row": 0,
      "col": 0,
      "size_x": 12,
      "size_y": 8,
      "parameter_mappings": [
        {
          "parameter_id": "param1",
          "card_id": {question_id},
          "target": ["dimension", ["field", "created_date", {"base-type": "type/Date"}], {"stage-number": 0}]
        }
      ]
    }
  ]
}
```

**⚠️ parameter_mappings 格式要点**:

正确的 `target` 格式必须包含 3 个元素：
```json
[
  "dimension",
  ["field", "field_name", {"base-type": "type/Date"}],
  {"stage-number": 0}
]
```

| 元素 | 说明 | 示例 |
|------|------|------|
| 第1个 | 类型标识 | `"dimension"` |
| 第2个 | field 定义 | `["field", "created_date", {"base-type": "type/Date"}]` |
| 第3个 | stage 信息 | `{"stage-number": 0}` |

**常见错误**:
```json
// ❌ 错误 - 缺少 stage-number
["dimension", ["field", "created_date", {"base-type": "type/Date"}], null]

// ❌ 错误 - 缺少 base-type
["dimension", ["field", "created_date", null], {"stage-number": 0}]

// ✅ 正确
["dimension", ["field", "created_date", {"base-type": "type/Date"}], {"stage-number": 0}]
```

**注意**:
- 卡片位置用负数 id (如 -1, -2)
- `parameter_mappings` 要正确绑定筛选器
- 布局: 24格宽，合理分配

---

## 阶段6：数据验证 (关键！)

### 方法

```bash
# 1. 用原SQL查询
POST /api/dataset
{
  "type": "native",
  "native": {"query": "原SQL"},
  "database": {database_id}
}

# 2. 用KMB查询
POST /api/card/{id}/query

# 3. 对比关键指标值
```

### 对比指标

| 指标 | 原SQL结果 | KMB结果 | 差异 |
|------|-----------|---------|------|
| 访客数 | 10000 | 10000 | ✅ |
| 有效访客数 | 8000 | 8000 | ✅ |
| 新访客数 | 3000 | 3000 | ✅ |
| 注册数 | 500 | 500 | ✅ |

**原则**: 差异应该在 0 或极小范围内

### 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 数值不一致 | 时间字段格式不一致 | Model 中加 `date_format` 预处理 |
| NULL 导致差异 | coalesce 处理缺失 | SQL 中加 `coalesce(field, 0)` |
| 条件逻辑差异 | case vs if | MBQL 用 `case`，SQL 用 `if` |

---

## ⚠️ 关键注意点 (常见错误)

| ❌ 错误 | ✅ 正确做法 |
|---------|------------|
| 批量统一所有 Questions 的 MBQL | 每个 Question 必须根据原 SQL **独立配置 breakout** |
| 忽略原前端配置，统一用模板 | 必须严格按 `graphType`/`legendFilterList`/`yAxisIndex` 还原 |
| aggregation 和展示层混淆 | 数据层建全指标(9个)，展示层只选需要(2个) |
| 不做数据验证 | **必须**用 API 对比原 SQL 和 KMB 数据 |
| 可视化配置用缓存猜 | 必须用 API 获取当前配置确认 |

---

## 🔧 API 工具方法

```python
import requests

METABASE_URL = "https://kmb.qunhequnhe.com"
API_KEY = "mb_xxx..."
headers = {"X-Api-Key": API_KEY}

# 获取配置
requests.get(f"{METABASE_URL}/api/card/{id}", headers=headers)

# 更新配置
requests.put(
    f"{METABASE_URL}/api/card/{id}",
    headers=headers,
    json={"visualization_settings": {...}}
)

# 执行查询
requests.post(f"{METABASE_URL}/api/card/{id}/query", headers=headers)
```

---

*最后更新: 2026-03-19* - 新增 Collection 485 实战修复案例

---

## 📚 实战案例: Collection 485 批量修复 (2026-03-19)

### 背景
Collection 485 下有 14 个 Traffic Questions，迁移后发现配置不规范，进行批量修复。

### 修复的问题清单

| 问题类型 | 影响 Question | 修复方法 |
|---------|--------------|---------|
| **dimensions 格式错误** | 4954, 4955, 4961, 4964 | 简化为 `["created_date"]` 格式 |
| **series_settings 不匹配** | 4973 | 移除多余指标，确保与 `graph.metrics` 一致 |
| **缺少 series_settings** | 4962, 4963 (Pie) | 添加空配置 `{}` |
| **转化率无百分比格式** | 4957, 4958 | 添加 `column_settings` + `number_style: percent` |
| **重复 Model** | 4950 | 归档旧版本，统一使用 4952 |

### 具体修复规范

#### 1. dimensions 格式修复
```json
// ❌ 错误 (完整 field 数组)
"graph.dimensions": [
  ["field", "created_date", {"base-type": "type/Date"}],
  ["field", "ads_channel_classify", {"base-type": "type/Text"}]
]

// ✅ 正确 (简化为字段名)
"graph.dimensions": ["created_date", "ads_channel_classify"]
```

#### 2. series_settings 匹配修复
```json
// ❌ 错误 - series 有多余指标
"graph.metrics": ["有效访客数", "访客数"],
"series_settings": {
  "有效访客数": {"axis": "left", "display": "line"},
  "访客数": {"axis": "left", "display": "line"},
  "新访客数": {}  // ❌ 多余的，metrics 里没有
}

// ✅ 正确 - 完全一致
"graph.metrics": ["有效访客数", "访客数"],
"series_settings": {
  "有效访客数": {"axis": "left", "display": "line"},
  "访客数": {"axis": "left", "display": "line"}
}
```

#### 3. 转化率百分比格式 (MixLineBar 必需)
```json
{
  "graph.dimensions": ["created_date"],
  "graph.metrics": ["新访客注册转化率", "新访客注册数", "新访客数"],
  "graph.show_values": true,
  "series_settings": {
    "新访客注册转化率": {"axis": "right", "display": "line"},
    "新访客注册数": {"axis": "left", "display": "bar"},
    "新访客数": {"axis": "left", "display": "bar"}
  },
  "column_settings": {
    "[\"name\",\"新访客注册转化率\"]": {"number_style": "percent"}
  }
}
```

#### 4. Pie 图表 series_settings
```json
// Pie 图表也需要 series_settings，可以为空
{
  "graph.dimensions": ["ads_channel_classify"],
  "graph.metrics": ["新访客数"],
  "series_settings": {
    "新访客数": {}  // ✅ 空配置也可以
  }
}
```

### 自查三部分 (修复后必须)

#### 第一部分：API 配置检查
```bash
# 1. 检查 dimensions 格式
curl -sL "https://kmb.qunhequnhe.com/api/card/4956" \
  -H "x-api-key: $API_KEY" | jq '.visualization_settings["graph.dimensions"]'
# 期望: ["created_date"] ✅
# 错误: [["field", ...]] ❌

# 2. 检查 series_settings 匹配
curl -sL "https://kmb.qunhequnhe.com/api/card/4956" \
  -H "x-api-key: $API_KEY" | jq '{
  metrics: .visualization_settings["graph.metrics"],
  series_keys: .visualization_settings.series_settings | keys
}'
# 期望: metrics 和 series_keys 完全一致 ✅

# 3. 检查转化率百分比
curl -sL "https://kmb.qunhequnhe.com/api/card/4957" \
  -H "x-api-key: $API_KEY" | jq '.visualization_settings.column_settings'
# 期望: 有 {"[\"name\",\"转化率\"]": {"number_style": "percent"}} ✅
```

#### 第二部分：浏览器截图验证
```bash
# 打开 Question 并截图
browser open "https://kmb.qunhequnhe.com/question/4956"
browser screenshot
```

检查清单：
- [ ] 图表正常渲染，无报错
- [ ] 图例显示正确（名称、数量与配置一致）
- [ ] 数值格式正确（百分比显示为 25% 而不是 0.25）
- [ ] MixLineBar 左右轴分配正确（数量左轴，转化率右轴）

#### 第三部分：Dashboard 整体检查
```bash
# 检查 Dashboard 卡片配置
curl -sL "https://kmb.qunhequnhe.com/api/dashboard/404" \
  -H "x-api-key: $API_KEY" | jq '.dashcards | length'

# 截图验证
browser open "https://kmb.qunhequnhe.com/dashboard/404"
browser screenshot
```

### 批量修复脚本

```bash
#!/bin/bash
# Collection 485 批量检查脚本

COLLECTION_ID=485
API_KEY="mb_xxx..."

echo "=== Collection $COLLECTION_ID 批量检查 ==="

# 获取所有 Card
cards=$(curl -sL "https://kmb.qunhequnhe.com/api/collection/$COLLECTION_ID/items" \
  -H "x-api-key: $API_KEY" | jq -r '.data[] | select(.model == "card" and (.archived // false) == false) | .id')

for id in $cards; do
  echo ""
  echo "--- Card $id ---"
  
  config=$(curl -sL "https://kmb.qunhequnhe.com/api/card/$id" -H "x-api-key: $API_KEY")
  name=$(echo $config | jq -r '.name')
  echo "Name: $name"
  
  # 检查 dimensions
  dims=$(echo $config | jq -r '.visualization_settings["graph.dimensions"] // []')
  first_dim=$(echo $dims | jq -r '.[0] // empty')
  if [[ "$first_dim" == "["* ]]; then
    echo "  ❌ dimensions: 格式错误 (数组格式)"
  else
    echo "  ✅ dimensions: 格式正确"
  fi
  
  # 检查 series_settings 匹配
  metrics=$(echo $config | jq -r '.visualization_settings["graph.metrics"] // [] | sort')
  series=$(echo $config | jq -r '.visualization_settings.series_settings // {} | keys | sort')
  
  if [ "$metrics" == "$series" ]; then
    echo "  ✅ series_settings: 匹配"
  else
    echo "  ❌ series_settings: 不匹配"
    echo "    metrics: $metrics"
    echo "    series: $series"
  fi
done
```

### 修复成果

| 资源 | 修复前 | 修复后 |
|------|--------|--------|
| **Question** | 14 个，多个配置错误 | 14 个，全部配置正确 ✅ |
| **Model** | 2 个重复 (4950, 4952) | 1 个 (4952)，4950 已归档 ✅ |
| **Dashboard** | 12 个卡片 | 12 个卡片，布局正常 ✅ |

---

## 📚 实战案例: TOP N 查询的 MBQL JOIN 重构 (2026-03-20)

### 背景
小站的 "Country Distribution Top 20" 和 "new visitor country distribution" 图表使用 SQL 子查询来筛选 TOP20 国家，然后按时间展示趋势。需要重构为 Metabase 数据建模逻辑。

### 原 SQL 逻辑
```sql
-- 主查询只保留 TOP20 国家的数据
WHERE fst_visit_country_sc IN (
    -- 子查询：计算各国新访客数，取 TOP20
    SELECT fst_visit_country_sc
    FROM (
        SELECT 
            fst_visit_country_sc,
            COUNT(DISTINCT CASE 
                WHEN (fst_registered_time IS NULL OR DATE_FORMAT(fst_registered_time, '%Y%m%d') = created_day)
                     AND COALESCE(DATE_FORMAT(fst_visit_coohom_time, '%Y%m%d'), created_day) = created_day 
                THEN qhdi 
            END) as new_visitor_cnt
        FROM dwb_coohom_user_visit_register_i_d
        WHERE ds BETWEEN '20260216' AND '20260301'
          AND !(ads_channel_classify = 'direct' AND fst_visit_country_sc = '美国')
          AND fst_visit_ua NOT IN ('meta-externalads/1.1...', 'Mozilla/5.0...')
        GROUP BY fst_visit_country_sc
    ) a
    ORDER BY new_visitor_cnt DESC
    LIMIT 20
)
```

### 重构方案: 两步建模 + MBQL JOIN

**核心原则**: 当两个 Question 的子查询逻辑不一致时，不能复用已有的 Question A，必须新建。

| 图表 | Question A | Question B | 能否复用 |
|------|-----------|-----------|---------|
| Country Distribution Top 20 (4955) | 5240 (总访客数 TOP20) | 4955 (JOIN 5240) | - |
| new visitor country distribution (4961) | 需新建 5553 (新访客数 TOP20) | 4961 (JOIN 5553) | ❌ 不能复用 5240 |

**差异分析**:
- 5240: 按总访客数排序，仅排除 "未知"
- 4961 需要: 按新访客数排序，额外过滤美国 direct + 特定 UA

### 实现步骤

#### Step 1: 创建 Question A' (ID: 5553)
```bash
POST /api/card
{
  "name": "【4961辅助】TOP20 New Visitor Countries",
  "type": "question",
  "collection_id": 485,
  "dataset_query": {
    "type": "query",
    "database": 4,
    "query": {
      "source-table": "card__4952",
      "filter": [
        "and",
        ["!=", ["field", "fst_visit_country_sc"], "未知"],
        ["not", ["and",
          ["=", ["field", "ads_channel_classify"], "direct"],
          ["=", ["field", "fst_visit_country_sc"], "美国"]
        ]],
        ["!=", ["field", "fst_visit_ua"], "meta-externalads/1.1..."],
        ["!=", ["field", "fst_visit_ua"], "Mozilla/5.0...Chrome/126..."]
      ],
      "breakout": [["field", "fst_visit_country_sc"]],
      "aggregation": [
        ["aggregation-options",
          ["distinct", ["case", [[...新访客计算逻辑...]], ["field", "qhdi"]]]],
          {"name": "新访客数"}
        ]
      ],
      "order-by": [["desc", ["aggregation", 0]]],
      "limit": 20
    }
  }
}
```

#### Step 2: 更新 Question B (4961) 使用 MBQL JOIN
```bash
PUT /api/card/4961
{
  "dataset_query": {
    "query": {
      "source-table": "card__4952",
      "joins": [
        {
          "source-table": "card__5553",
          "alias": "TOP20 New Visitor Countries",
          "strategy": "inner-join",
          "condition": [
            "=",
            ["field", "fst_visit_country_sc"],
            ["field", "fst_visit_country_sc", {"join-alias": "TOP20 New Visitor Countries"}]
          ]
        }
      ],
      "breakout": [
        ["field", "created_date"],
        ["field", "fst_visit_country_sc"]
      ],
      "aggregation": [...]
    }
  }
}
```

### 验证结果
```bash
# 检查 JOIN 数量
curl /api/card/4961 | jq '.dataset_query.query.joins | length'
# → 1 ✅

# 查询验证
curl -X POST /api/card/4961/query | jq '.data.rows | map(.[1]) | unique | length'
# → 20 ✅ (正好 20 个国家)
```

### 关键经验

1. **子查询逻辑不一致时，必须新建 Question A'**
   - 不能为了省事复用已有的 5240
   - 4961 的新访客计算 + 特殊过滤条件与 5240 完全不同

2. **复杂 CASE 聚合在 MBQL 中的写法**
   ```json
   ["aggregation-options",
     ["distinct",
       ["case",
         [[["and",
             ["or", ["is-null", ["field", "fst_registered_time_day"]], ["=", ...]],
             ["=", ["field", "fst_visit_coohom_time_day_or_created"], ["field", "created_day"]]
           ],
           ["field", "qhdi"]
         ]]
       ]
     ],
     {"name": "新访客数"}
   ]
   ```

3. **JOIN 条件的正确格式**
   ```json
   ["=",
     ["field", "fst_visit_country_sc", {"base-type": "type/Text"}],
     ["field", "fst_visit_country_sc", {"base-type": "type/Text", "join-alias": "别名"}]
   ]
   ```

4. **数据建模链路**
   ```
   Model (4952: 清洗数据)
       → Question A' (5553: 派生 TOP20 新访客国家) - MBQL
       → Question B (4961: 分析时间趋势，通过 JOIN 关联) - MBQL
   ```

### 与 4955 重构的对比

| 维度 | 4955 | 4961 |
|------|------|------|
| Question A | 5240 (MBQL) | 5553 (MBQL) |
| 聚合指标 | 总访客数 | 新访客数 (CASE) |
| 特殊过滤 | 仅排除 "未知" | + 美国 direct + UA 过滤 |
| 能否复用 | - | ❌ 不能复用 5240 |
| 链路 | Model → MBQL A → MBQL B | Model → MBQL A' → MBQL B |

---

*实战记录来源: memory/2026-03-20.md*
*最后更新: 2026-03-20*

---

## 📒 Memory 整合（2026-03-12 ~ 2026-03-25）

> 本节整合 OpenClaw workspace 的阶段性工作记录，用于沉淀“做过什么、踩过什么坑、如何复用”。
>
> 口径说明：
> - 本节是**经验记录**；强约束以 `rules/*` 为准。
> - 当前执行基线：**默认必须 Model + MBQL，不把原生 SQL 作为常规回退**（详见 `rules/api-standards.md`）。

### 目录
1. 2026-03-12 - Metabase 项目完成
2. 2026-03-13 - Snapit 分析与漏斗实现
3. 2026-03-17 - AARRR 日报与 DataSpace 迁移
4. 2026-03-18 - Dashboard 配置与 MixLineBar
5. 2026-03-19 - KMB Skill 自动更新机制
6. 2026-03-24 - 全访客明细迁移
7. 2026-03-25 - 核心原则与最佳实践

---

### 1) 2026-03-12 - Metabase 项目完成

#### 今日核心工作
- 深度分析 Dashboard 312（coohom-new）结构。
- 理解 Model 3953（意向用户付费 model）的“SQL 明细层宽表”设计。
- 解析 17 个 Questions 的 MBQL 配置。
- 抽取核心业务指标：支付成功率、客单价、新签/升级/召回。

#### 文档与实战产出
- 编写 MBQL 构建指南（Field/Filter/Aggregation/Expressions/Joins/Source-query）。
- 创建并验证：
  - Question 4371（初版，单位混用）
  - Question 4374（修正版，转化率百分比）
  - Dashboard 337（引用新 Questions）
- 结果校验：新签 7.83%，召回 55.31%，升级 19.76%。

#### 关键认知
- Model 层负责“数据准备与预处理”；Question 层负责“聚合与展示”。
- MBQL 主链路：
  `source-table → joins → filter → breakout → aggregation → expressions → order-by`

---

### 2) 2026-03-13 - Snapit 分析与漏斗实现

#### 业务背景
Snapit 是 Coohom 的 AI 图片生成工具，核心覆盖任务系统、赠金/积分、消耗与收入。

#### 创建资源
| 类型 | ID | 名称 |
|------|----|------|
| Collection | 456 | test |
| Metric | 4468 | 日活用户数 DAU |
| Question | 4469 | 任务成功率分析 |
| Question | 4470 | 风格偏好排行 |
| Dashboard | 347 | Snapit Test Analysis |

#### MBQL 新知识点
- 复合 Join 条件（`and` 组合多字段匹配）。
- `count-where` 用于条件计数。
- alias 简化长字段路径。
- 聚合字段中文 display-name。

#### 踩坑与纠偏
1. Question 硬编码 `time-interval` 与 Dashboard 参数冲突。
2. 删除旧 Question 后未同步更新 Dashboard 引用。
3. 参数映射缺少完整 `join-alias`。

**纠偏结论**：
- MBQL Question 通常不需要 `parameters`。
- `template-tags` 是 Native SQL Question 的参数机制。

---

### 3) 2026-03-17 - AARRR 日报与 DataSpace 迁移

#### 自动化进展
- 建立 AARRR 每日 17:00 推送。
- 修复 Activation/Retention 对比周期（考虑 1 周转化延迟）。
- WAU 改为表格；Revenue 改为 1/2/3 层级格式。

#### DataSpace → KMB 迁移策略（阶段版）
- 当时采用：先 Native SQL 快速迁移，再逐步重构 Model + MBQL。
- 当前已对齐为：默认必须 Model + MBQL；`UNION ALL` 拆分多 Question、动态时间走 Dashboard 筛选、缺字段先在 Model 预加工；仅在完全无法解决且记录原因时允许原生 SQL 例外。

#### i表 / s表 规则
| 表类型 | Model 层筛选 | 原因 |
|--------|-------------|------|
| i表（增量） | ❌ 一般不加 ds | 保留历史增量，全量可追溯 |
| s表（快照） | ✅ 选快照 ds（通常昨日） | 避免多日快照叠加导致膨胀 |

---

### 4) 2026-03-18 - Dashboard 配置与 MixLineBar

#### 高发问题与修复
| 问题 | 原因 | 修复 |
|------|------|------|
| UI 显示过多指标 | `series_settings` 配置了全部指标 | 仅配置需要展示的指标 |
| 转化率未显示百分比 | 缺少 `column_settings` | 添加 `number_style: percent` |
| MixLineBar 展示异常 | 未区分 line/bar 与左右轴 | 明确 `display` + `axis` |
| `graph.dimensions` 格式错误 | 使用完整 field 数组 | 简化为字段名数组（如 `["created_date"]`） |
| aggregation 不完整 | 只建了部分指标 | 按口径补齐完整指标集 |

#### MixLineBar 标准模板
```json
{
  "graph.metrics": ["转化率", "数量1", "数量2"],
  "series_settings": {
    "转化率": {"display": "line", "axis": "right"},
    "数量1": {"display": "bar", "axis": "left"},
    "数量2": {"display": "bar", "axis": "left"}
  },
  "column_settings": {
    "[\"name\",\"转化率\"]": {"number_style": "percent"}
  }
}
```

---

### 5) 2026-03-19 - KMB Skill 自动更新机制

#### 机制建设
- 新增 `scripts/update_skill.sh` 更新检查脚本。
- 更新 `TOOLS.md` 记录 KMB Skill 更新流程。
- 更新 `SKILL.md` 链接（迁移指南增强）。

#### TOP N 查询建模沉淀
采用“两步建模 + MBQL JOIN”：
1. Question A：先产出 30 天 TOP20 集合。
2. Question B：基于 MBQL JOIN 做趋势分析。

关键 JOIN 结构：
```json
{
  "source-table": "card__4952",
  "joins": [
    {
      "source-table": "card__5240",
      "alias": "TOP20 Countries List",
      "strategy": "inner-join",
      "condition": [
        "=",
        ["field", "fst_visit_country_sc"],
        ["field", "fst_visit_country_sc", {"join-alias": "TOP20 Countries List"}]
      ]
    }
  ]
}
```

---

### 6) 2026-03-24 - 全访客【日】landing page 明细迁移

#### 交付资源
- Model：`landing_page_visit_register_daily`（ID: 5943）
- Collection：512
- Question：5944（分渠道）
- Question：5945（不分渠道）

#### 关键链接
- Dashboard: `https://kmb.qunhequnhe.com/dashboard/480`
- Model: `https://kmb.qunhequnhe.com/question/5943`
- Question（分渠道）: `https://kmb.qunhequnhe.com/question/5950`

---

### 7) 2026-03-25 - 核心原则与最佳实践

#### 总原则
> 能在 Model 层（SQL）完成的，不在 Question 层用复杂 MBQL 重复实现。

#### 表类型处理（复核版）
| 表类型 | 后缀 | 处理方式 |
|--------|------|----------|
| i表 | `_i_d` | 增量表，一般不限制 ds，由 Dashboard/查询条件控制 |
| s表 | `_s_d` | 快照表，必须选择快照 ds（通常昨日） |

#### 关键教训
1. **Model 保留原始字段名**
   - 原 SQL `GROUP BY` 字段（如 `ads_channel_classify`）不要随意改名。
2. **breakout 对齐 GROUP BY 语义**
   - breakout 字段来自原 SQL 的 group by，不在 MBQL 层补复杂 CASE。
3. **排序字段对齐 ORDER BY**
   - 在 Model 预计算排序字段，Question 直接引用。
4. **强制对比验证**
   - 字段名、breakout、aggregation 名称/数量、order_by 索引逐项核对。

#### 时间字段类型
- ❌ 错误：使用 Text 时间字段做聚合维度
- ✅ 正确：在 Model 中转 date 类型（如 `STR_TO_DATE(created_day, '%Y%m%d') AS ds_time`）

---

### 附：迁移执行检查清单（可复用）

每次创建/重构后，按顺序执行：

- [ ] Model 字段名与原 SQL 语义一致
- [ ] breakout 与原 SQL GROUP BY 一一对应
- [ ] aggregation 数量、名称、口径一致
- [ ] order_by 指向正确 aggregation
- [ ] 时间字段为可聚合 date 类型（用于筛选器/时间粒度）
- [ ] Dashboard 图例仅暴露必要指标
- [ ] 比率字段配置百分比显示
- [ ] 通过 `/api/card/:id/query` 做可运行性验证
- [ ] 与对照版本做结果抽样比对

*Memory 整合补充: 2026-03-26*
