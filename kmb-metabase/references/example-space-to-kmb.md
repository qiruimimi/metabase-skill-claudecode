# 小站 SQL 到 KMB 迁移完整示例

> 基于 Traffic Collection 485 的实战经验

---

## 场景：国家分布 TOP20 时间趋势图

### 小站原始配置

**Page**: 53823 (Traffic Overview)  
**Graph**: Country Distribution Top 20  
**Graph Type**: LineSimple (时间趋势图)  
**需求**: 展示访客数 TOP20 国家随时间的变化

### 原始 SQL 逻辑

```sql
-- 小站原始 SQL 概念
SELECT 
    created_day,
    fst_visit_country_sc,
    COUNT(DISTINCT qhdi) as 访客数,
    COUNT(DISTINCT CASE WHEN ... THEN qhdi END) as 有效访客数,
    ...
FROM dwb_coohom_user_visit_register_i_d
WHERE created_day >= '20250301'
GROUP BY created_day, fst_visit_country_sc
ORDER BY 访客数 DESC
```

**问题**: 返回所有国家，超过 100 series 限制

---

## 第一步：创建 Model (数据层)

### 分析 SQL

| 原始 SQL 元素 | Model 处理 |
|--------------|-----------|
| SELECT 字段 | 保留原始字段，不做聚合 |
| WHERE ds 筛选 | **不添加** (Model 保留全量) |
| GROUP BY | **不添加** (Model 不做聚合) |
| 计算字段 | 在 Model 中预处理 (如 str_to_date) |

### Model SQL

```sql
SELECT 
    qhdi,
    created_day,
    str_to_date(created_day, '%Y%m%d') as created_date,
    visit_user_id,
    fst_registered_time,
    date_format(fst_registered_time, '%Y%m%d') as fst_registered_time_day,
    fst_visit_coohom_time,
    date_format(fst_visit_coohom_time, '%Y%m%d') as fst_visit_coohom_time_day,
    -- 处理NULL值，用于新访客判断
    coalesce(date_format(fst_visit_coohom_time, '%Y%m%d'), created_day) 
        as fst_visit_coohom_time_day_or_created,
    register_user_id,
    ads_channel_classify,
    fst_visit_country_sc,
    fst_visit_country_en,
    ...
FROM hive_prod.exabrain.dwb_coohom_user_visit_register_i_d
-- Model 不添加 WHERE 筛选，保留全量数据
```

### 创建 Model API

```bash
POST /api/card
{
  "type": "model",
  "name": "traffic_user_visit_register",
  "dataset_query": {
    "type": "native",
    "native": {
      "query": "SELECT ... FROM hive_prod.exabrain.dwb_coohom_user_visit_register_i_d",
      "template-tags": {}
    },
    "database": 4
  },
  "collection_id": 485
}
```

**结果**: Model ID = 4952

---

## 第二步：创建 Question A (派生指标 - TOP20 国家)

### 目的
从 Model 中找出访客数前 20 的国家列表

### MBQL 配置

```json
{
  "name": "TOP20 Countries List",
  "display": "table",
  "dataset_query": {
    "database": 4,
    "type": "query",
    "query": {
      "source-table": "card__4952",  // 引用 Model
      
      // 过滤条件
      "filter": [
        "!=", 
        ["field", "fst_visit_country_sc", {"base-type": "type/Text"}], 
        "未知"
      ],
      
      // 分组：按国家
      "breakout": [
        ["field", "fst_visit_country_sc", {"base-type": "type/Text"}]
      ],
      
      // 聚合：访客数
      "aggregation": [
        ["aggregation-options", 
         ["distinct", ["field", "qhdi", {"base-type": "type/Text"}]], 
         {"name": "访客数"}
        ]
      ],
      
      // 排序：按访客数降序
      "order-by": [
        ["desc", ["aggregation", 0]]
      ],
      
      // 限制：只取前20
      "limit": 20
    }
  },
  "collection_id": 485
}
```

### 结果

```bash
POST /api/card
# 返回 Question ID: 5240
```

**查询结果**:
```
fst_visit_country_sc | 访客数
--------------------|--------
印度                | 7886733
韩国                | 4924940
美国                | 3177123
...                 | ...
```

---

## 第三步：创建 Question B (最终分析 - 时间趋势)

### 目的
查询 TOP20 国家的时间趋势，使用 JOIN 关联 Question A

### 关键点
- **不是硬编码 filter**: `["in", ["field", "country"], "印度", "韩国", ...]` ❌
- **而是 MBQL JOIN**: `joins: [{source-table: "card__5240", strategy: "inner-join"}]` ✅

### MBQL 配置

```json
{
  "name": "Country Distribution Top 20",
  "display": "line",
  "dataset_query": {
    "database": 4,
    "type": "query",
    "query": {
      // 主表：Model
      "source-table": "card__4952",
      
      // JOIN 关联 Question A
      "joins": [
        {
          "fields": ["fst_visit_country_sc"],
          "source-table": "card__5240",  // 引用 Question A
          "condition": [
            "=",
            ["field", "fst_visit_country_sc", {"base-type": "type/Text"}],  // Model 字段
            ["field", "fst_visit_country_sc", {"base-type": "type/Text", "join-alias": "TOP20 Countries List"}]  // Question A 字段
          ],
          "alias": "TOP20 Countries List",
          "strategy": "inner-join"
        }
      ],
      
      // 分组：时间 + 国家
      "breakout": [
        ["field", "created_date", {"base-type": "type/Date"}],
        ["field", "fst_visit_country_sc", {"base-type": "type/Text"}]
      ],
      
      // 聚合：访客数、有效访客数、注册数
      "aggregation": [
        ["aggregation-options", 
         ["distinct", ["field", "qhdi", {"base-type": "type/Text"}]], 
         {"name": "访客数"}
        ],
        ["aggregation-options", 
         ["distinct", ["field", "visit_user_id", {"base-type": "type/BigInteger"}]], 
         {"name": "有效访客数"}
        ],
        ["aggregation-options", 
         ["distinct", ["field", "register_user_id", {"base-type": "type/BigInteger"}]], 
         {"name": "注册数"}
        ]
      ]
    }
  },
  
  // 可视化配置
  "visualization_settings": {
    "graph.dimensions": ["created_date", "fst_visit_country_sc"],
    "graph.metrics": ["访客数"],
    "series_settings": {
      "访客数": {"display": "line"}
    },
    "stackable.stack_type": "stacked"
  },
  
  "collection_id": 485
}
```

### 创建 API

```bash
PUT /api/card/4955
{
  // 上述配置
}
```

---

## 完整数据建模链路

```
┌─────────────────────────────────────────────────────────┐
│  小站原始 SQL                                            │
│  SELECT created_day, country, COUNT(*)                   │
│  FROM table                                              │
│  GROUP BY created_day, country                           │
│  (返回所有国家，超过100 series)                            │
└─────────────────────────────────────────────────────────┘
                            ↓ 重构
┌─────────────────────────────────────────────────────────┐
│  Step 1: Model (4952) - 数据层                           │
│  - 清洗原始数据                                           │
│  - 预处理字段 (str_to_date, coalesce)                     │
│  - 不做聚合，保留全量                                      │
└─────────────────────────────────────────────────────────┘
                            ↓ 派生
┌─────────────────────────────────────────────────────────┐
│  Step 2: Question A (5240) - 派生指标层                   │
│  - 从 Model 计算 TOP20 国家                               │
│  - breakout: [country]                                    │
│  - aggregation: [distinct(qhdi)]                          │
│  - order-by: [desc(aggregation)]                          │
│  - limit: 20                                              │
│  - filter: country != "未知"                              │
└─────────────────────────────────────────────────────────┘
                            ↓ JOIN 关联
┌─────────────────────────────────────────────────────────┐
│  Step 3: Question B (4955) - 分析层                       │
│  - source-table: Model (4952)                             │
│  - joins: [{                                               │
│      source-table: Question A (5240),                     │
│      strategy: "inner-join",                              │
│      condition: Model.country = QuestionA.country         │
│    }]                                                     │
│  - breakout: [created_date, country]                      │
│  - aggregation: [distinct(qhdi), ...]                     │
│  - 结果: 正好 20 个国家的时间趋势                          │
└─────────────────────────────────────────────────────────┘
```

---

## 常见错误和解决方案

### 错误 1：超过 100 series

**错误信息**:
```
This chart contains more than 100 series...
```

**原因**:
```json
// 错误：双维度 breakout 产生大量组合
"breakout": [
  ["field", "created_date"],    // 30天
  ["field", "country"]            // 200+ 国家
]
// 30 × 200 = 6000+ series
```

**解决**:
- 方法 A: 添加 `limit: 20` (只显示前20)
- 方法 B: 使用 **两步建模 + JOIN** (推荐) ✅

---

### 错误 2：硬编码 filter 不是结构关联

**错误做法**:
```json
// 硬编码国家列表 - 不是真正的结构关联
"filter": [
  "in", 
  ["field", "country"], 
  "印度", "韩国", "美国", ...  // 硬编码 20 个国家
]
```

**问题**:
- Question A 结果变化时，Question B 不会自动更新
- 需要手动同步国家列表

**正确做法**:
```json
// 使用 MBQL JOIN - 真正的结构关联
"joins": [
  {
    "source-table": "card__5240",  // 引用 Question A
    "strategy": "inner-join",
    "condition": ["=", 
      ["field", "country"], 
      ["field", "country", {"join-alias": "TOP20"}]
    ]
  }
]
```

**优点**:
- Question A 更新时，Question B 自动同步
- 符合数据建模逻辑

---

### 错误 3：Question B 聚合逻辑错误

**错误**: 直接复制 Question A 的 aggregation 到 Question B

**理解**:
- **Question A**: 计算 TOP20 国家（按国家分组，聚合算访客数）
- **Question B**: 查询时间趋势（按时间+国家分组，聚合算访客数）

**正确**:
```json
// Question A: 只按国家分组
"breakout": [["field", "country"]]
"aggregation": [["distinct", ["field", "qhdi"]]]  // 算总访客数

// Question B: 按时间+国家分组
"breakout": [
  ["field", "created_date"],
  ["field", "country"]
]
"aggregation": [["distinct", ["field", "qhdi"]]]  // 算每天访客数
```

---

## 总结

| 步骤 | 对象 | 作用 | 关键技术 |
|------|------|------|---------|
| 1 | Model | 清洗数据，提供基础层 | Native SQL，预处理字段 |
| 2 | Question A | 派生指标 (TOP N) | MBQL breakout + aggregation + limit |
| 3 | Question B | 最终分析 (时间趋势) | MBQL joins (inner-join) |

### 核心原则

1. **Model 不做聚合** - 保留原始粒度
2. **Question 做分析** - 根据需求聚合
3. **TOP N 用两步建模** - Question A 算 TOP N，Question B 做 JOIN 分析
4. **结构关联用 JOIN** - 不用硬编码 filter

---

*示例来源: Traffic Collection 485 国家分布迁移*
*日期: 2026-03-19*
