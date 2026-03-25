# Dashboard 配置文档

记录 KMB 平台上重要 Dashboard 的结构和配置。

---

## Dashboard 139: GA投放词分析

**Dashboard ID:** 139
**名称:** 投放词数据总览
**用途:** GA 广告投放词效果分析

### Tabs 结构

| Tab ID | Tab 名称 | 说明 |
|--------|----------|------|
| 214 | 投放词数据总览 | 主要分析投放词效果 |
| 215 | campaign | Campaign 维度分析 |

### 核心 Card IDs

| Card ID | 名称 | 说明 |
|---------|------|------|
| 1724 | 投放词列表 | 所有投放词明细 |
| 1726 | Campaign列表 | Campaign 列表 |
| 1732 | LTV/CAC | 用户生命周期价值/获客成本 |
| 1731 | ROAS 7天 | 7天广告支出回报率 |
| 1750 | ROAS 180天 | 180天广告支出回报率 |

### 核心指标

| 指标 | 字段名 | 说明 |
|------|--------|------|
| 投放花费($) | spend | GA广告花费 |
| 注册用户数 | registered_users | 通过投放注册的用户数 |
| LTV/CAC | ltv_cac_ratio | 用户生命周期价值/获客成本 |
| ROAS (7天) | roas_7d | 7天内广告支出回报率 |
| ROAS (180天) | roas_180d | 180天内广告支出回报率 |
| 次周留存数量 | retention_next_week | 进工具的留存用户数 |

### 筛选参数

| 参数 | 类型 | 说明 |
|------|------|------|
| 日期范围 | date | 数据时间范围 |
| 日期粒度 | granularity | day/week/month |
| 投放词筛选 | keyword | 指定投放词 |
| Campaign筛选 | campaign | 指定 Campaign |

---

## Dashboard 254: COOHOM折扣体系

**Dashboard ID:** 254
**名称:** COOHOM折扣体系
**Collection ID:** 396
**用途:** 折扣转化漏斗分析

### 核心 Card IDs

| Card ID | 名称 | 说明 |
|---------|------|------|
| 3228 | 有意向用户->支付成功 转化数据 | 转化漏斗主表 |
| 3267 | 有意向用户->支付成功 转化数据 - 分场景 | 分场景转化数据 |

---

## 常用 Card 速查

### 用户相关
| Card ID | 名称 |
|---------|------|
| - | (待补充) |

### 收入相关
| Card ID | 名称 |
|---------|------|
| - | (待补充) |

### 投放相关
| Card ID | 名称 |
|---------|------|
| 1724 | 投放词列表 |
| 1726 | Campaign列表 |
| 1731 | ROAS 7天 |
| 1732 | LTV/CAC |
| 1750 | ROAS 180天 |

---

## Dashboard 494: Revenue用户分层（新）

**Dashboard ID:** 494
**名称:** Revenue用户分层（新）- 迁移
**Collection ID:** 521
**来源:** Tesseract page/55074

### 核心 Card IDs

| Card ID | 名称 | 说明 |
|---------|------|------|
| 6122 | Model: pay_success_time 转换 | 提供 date 类型时间字段 |
| 6123 | Revenue每日汇总表(筛选器版) | 日汇总收入数据 |
| 6124 | Revenue账单分层单数(筛选器版) | 分层单数统计 |
| 6125 | Revenue每日收入分布(筛选器版) | 分层收入统计 |
| 6112, 6113, 6114, 6116 | (其他图表) | 待确认 |

### 筛选参数

| 参数 ID | 参数名称 | 类型 | 默认值 | 说明 |
|---------|----------|------|--------|------|
| param_date | 日期范围 | date/all-options | past2months~ | 近2月包含本月 |

### 参数映射关系

Tesseract Page/55074 的参数映射到 KMB Dashboard:

| Tesseract 参数 | KMB 参数 | KMB 默认值 | 说明 |
|----------------|----------|-----------|------|
| start_ds (MONDAY_OF_WEEK, -56) | param_date | past12months~ | 近12月 |
| end_ds (TODAY, 0) | (合并到date范围) | past2months~ | 近2月包含本月 |

### 关键发现

1. **Dashboard 筛选器关联失败问题**: 如果 Question 使用字符串类型时间字段（如 `pay_success_day`），无法与 Dashboard date 筛选器关联。需要使用 date 类型字段（如 `pay_success_time`）。
2. **解决方案**: 创建 Model 使用 `STR_TO_DATE()` 转换时间字段为 date 类型。

---

## Dashboard 404: Traffic Overview（参考标准）

**Dashboard ID:** 404
**名称:** Traffic Overview Dashboard
**用途:** 流量渠道分析

### 筛选参数（参考配置）

| 参数 ID | 参数名称 | type | sectionId | default |
|---------|----------|------|-----------|---------|
| param_date | 日期范围 | date/all-options | date | past30days |
| param_channel | 渠道类型 | string/= | string | [多选] |
| param_country_sc | 国家（中文） | string/= | string | - |
| param_utm | utm_source | string/= | string | - |

### parameter_mappings 示例

```json
{
  "parameter_mappings": [
    {
      "parameter_id": "param_date",
      "card_id": 4964,
      "target": [
        "dimension",
        ["field", "created_date", {"base-type": "type/Date"}],
        {"stage-number": 0}
      ]
    },
    {
      "parameter_id": "param_channel",
      "card_id": 4964,
      "target": [
        "dimension",
        ["field", "ads_channel_classify", {"base-type": "type/Text"}],
        {"stage-number": 0}
      ]
    }
  ]
}
```

---

## Dashboard 参数配置指南

### 标准参数结构

创建 Dashboard 筛选器时，使用以下标准格式：

```json
{
  "parameters": [
    {
      "name": "日期范围",
      "slug": "date_range",
      "id": "param_date",
      "type": "date/all-options",
      "sectionId": "date",
      "default": "past2months~"
    }
  ]
}
```

**必需字段：**
| 字段 | 推荐值 | 说明 |
|------|--------|------|
| `type` | `date/all-options` | 日期筛选器类型 |
| `sectionId` | `date` | 日期类型 section |

### 日期默认值转换（Tesseract → KMB）

**Tesseract Page 参数 default 格式：**
```json
{"relativeTimeReference":"MONDAY_OF_WEEK","offset":-56,"value":""}
```

**转换规则：**
| Tesseract relativeTimeReference | offset | KMB default | 说明 |
|----------------------------------|--------|-------------|------|
| `MONDAY_OF_WEEK` | -56 | `past12months~` | 近12月（56周） |
| `MONDAY_OF_WEEK` | -28 | `past6months~` | 近6月（28周） |
| `TODAY` | 0 | `past2months~` | 近2月包含本月 |
| `TODAY` | -1 | (不需要) | 昨天，KMB 默认今天 |

**格式说明：**
- `~` 结尾 = 包含本月
- 无 `~` = 不包含本月

**KMB 常用日期格式：**
| 格式 | 说明 |
|------|------|
| `"past30days"` | 过去30天 |
| `"past2months~"` | 近2月包含本月 |
| `"past6months~"` | 近6月包含本月 |
| `"past12months~"` | 近12月包含本月 |
| `"2024-01-01~2024-03-25"` | 固定日期范围 |

### Tesseract → KMB 迁移流程

1. **获取 Tesseract Page 参数**: `tesseract_mcp_beta::get_page` 获取 pageId
2. **分析参数**: 识别 page 级别参数（对应 Dashboard 筛选器）
3. **转换日期参数**: Tesseract relativeTime → KMB 相对时间格式
4. **创建 Dashboard 参数**: PUT `/api/dashboard/{id}` 设置 parameters
5. **配置参数映射**: 在 dashcards 的 parameter_mappings 中关联

### parameter_mappings 正确格式

```json
{
  "parameter_mappings": [
    {
      "parameter_id": "param_date",
      "card_id": 6124,
      "target": [
        "dimension",
        ["field", "pay_success_time", {"base-type": "type/Date"}],
        {"stage-number": 0}
      ]
    }
  ]
}
```

**常见错误：**
| 错误 | 正确 |
|------|------|
| 缺少 `card_id` | 必须包含 `card_id` |
| 有 `temporal-unit` | 移除 `temporal-unit` |
| 缺少 `stage-number` | 必须有 `{"stage-number": 0}` |
| `base-type` 不是 `type/Date` | 筛选器字段必须是 `type/Date` |

---

## 数据库信息

| 数据库 ID | 名称 | 引擎 |
|-----------|------|------|
| 4 | Hive_prod | hive-like |
| 5 | datacool-dim | mysql |

---

*最后更新: 2026-03-25*
