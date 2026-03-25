# Metabase 最佳实践 (MBQL)

记录 KMB (Metabase) 使用中的经验总结和最佳实践。

---

## 1. MBQL 条件聚合

### ❌ 错误: 使用 `if` 表达式
```json
{
  "aggregation": [
    ["sum", ["expression", "if(category = 'A', amount, 0)"]]
  ]
}
```

### ✅ 正确: 使用 `case` 表达式
```json
{
  "aggregation": [
    ["sum", ["case", [[["=", ["field", 123], "A"], ["field", 456]]]]]
  ]
}
```

**原因**: MBQL 中条件判断使用 `case`，不是 `if`。`case` 语法更标准，支持多条件分支。

---

## 2. 转化率计算

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

## 3. Model 层预处理 vs Question 层 MBQL（核心原则）

> **铁律：能用 SQL 在 Model 层解决的，不要在 Question 层用 MBQL 折腾！**

### 3.1 字段预处理 - 在 Model SQL 中完成

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

### 3.2 Group By 对应关系

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

### 3.3 聚合指标口径

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

### 3.4 排序处理

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

### 3.5 对照表：Model 层 vs Question 层

| 步骤 | Model 层（SQL） | Question 层（MBQL） |
|------|----------------|-------------------|
| **字段预处理** | CASE WHEN 计算分类、排序字段 | 直接用预计算好的字段 |
| **日期转换** | `STR_TO_DATE(ds, '%Y%m%d')` → `ds_time` | 直接用 `ds_time` |
| **别名** | SQL 中用中文别名 | 直接用中文别名引用 |
| **Group By** | SQL 中 `GROUP BY` | `breakout` 必须和 SQL 一致 |
| **Aggregation** | SQL 中聚合 | `max(分组字段)` + `distinct(指标)` |
| **Order By** | 预计算排序字段 | 直接用数字字段排序 |

### 3.6 时间字段处理（补充）

除上述原则外，时间字段也应在 Model 层预处理：

```sql
-- Model SQL 中定义多种时间粒度
SELECT
  STR_TO_DATE(ds, '%Y%m%d') AS ds_time,
  DATE_FORMAT(STR_TO_DATE(ds, '%Y%m%d'), '%Y-%u') AS week_start,
  DATE_FORMAT(STR_TO_DATE(ds, '%Y%m%d'), '%Y-%m') AS month_start
FROM table
```

Question 中直接使用：
```json
{
  "breakout": [
    ["field", "week_start", {"base-type": "type/Text"}]
  ]
}
```

**原因**:
- Model 层预处理保证计算逻辑统一
- 避免每个 Question 重复定义时间转换逻辑
- 查询性能更好
- 减少 MBQL 复杂度和出错概率

---

## 4. 可视化设计

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

## 5. Question 设计模式

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

## 6. 性能优化建议

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

## 7. 调试技巧

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

*最后更新: 2026-03-18*
