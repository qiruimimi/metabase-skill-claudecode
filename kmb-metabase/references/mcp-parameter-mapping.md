# Tesseract MCP 参数格式映射指南

> 本文档说明 Tesseract（数据小站）页面/图表参数如何映射到 Metabase（KMB）的筛选器格式。

---

## 参数类型对照表

| Tesseract Type | Tesseract 格式示例 | KMB 对应配置 |
|----------------|-------------------|--------------|
| DATE | `{"relativeTimeReference":"TODAY","offset":-14}` | `date/all-options` |
| ENUM（多选） | `"value1","value2"` | `string/=`，开启多选 |
| ENUM（单选） | `日` | `string/=`，关闭多选 |
| ANY | 自由文本 | `string/contains` 或 `string/=` |

---

## DATE 类型

### Tesseract 格式

```json
{
  "relativeTimeReference": "TODAY",
  "offset": -14,
  "value": ""
}
```

### 常用 relativeTimeReference 枚举

| 值 | 含义 |
|---|---|
| `TODAY` | 今天 |
| `MONDAY_OF_WEEK` | 本周周一 |
| `ABSOLUTE` | 绝对日期（此时 `value` 有具体日期值） |

### KMB 映射

在 KMB Dashboard/Card 中：
- 字段类型选择 `Date`
- 筛选器类型选择 `All Options`
- 默认值根据相对时间计算后的绝对日期填入，或保留为空由用户手动选择

---

## ENUM 类型

### Tesseract 格式

在 `get_page` / `get_graph` 返回的 `parameterList` 中，ENUM 类型参数通常包含：

```json
{
  "name": "data_type",
  "type": "ENUM",
  "defaultValue": "日",
  "config": "日\n周\n月"
}
```

`config` 字段以换行符 `\n` 分隔各个选项。

### 动态配置参数（dynamicConfig = true）

部分 ENUM 参数（如 `country_en`）的 `dynamicConfig` 为 `true`，其选项列表由 SQL 动态返回，不在 `config` 中写死。

处理方式：
1. 在 KMB 中使用关联字段（如 `country_sc`）作为级联筛选
2. 或直接用 `string/=` / `string/contains` 让用户手动输入

### KMB 映射

| 场景 | KMB 配置 |
|---|---|
| 单选 ENUM | `string/=`，多选开关关闭 |
| 多选 ENUM | `string/=`，多选开关开启 |
| 选项较多（如 50+ 个入口） | 考虑使用搜索框或 `string/contains` |

---

## ANY 类型

### Tesseract 格式

```json
{
  "name": "openposition2",
  "type": "ANY",
  "defaultValue": ""
}
```

### KMB 映射

- 字段类型：`string`
- 筛选器类型：`contains`（模糊匹配）或 `=`（精确匹配）
- 适合作为精准查询的文本输入框

---

## 页面参数 vs 图表参数

### 覆盖规则

Tesseract 中：
- 页面级参数通过 `graphParameterIdList` 关联到图表参数 ID
- 图表可以覆盖页面级参数的默认值（如 v1 图表默认 `version=v1`，v3 图表默认 `version=v3`）

### 迁移注意事项

1. 在 KMB Model/Question 层定义统一的模板变量
2. 在 Dashboard 层设置 Dashboard Filter，并绑定到各 Card
3. 若不同版本 Card 需要不同的固定过滤条件（如 version=v1/v3），可在 Card 自身 SQL 中写死 `WHERE version = 'v1'`，而不是依赖 Dashboard Filter
