# 常用 Card 目录

按业务场景分类的常用 Card 索引。

---

## 按场景分类

### 投放分析

| Card ID | 名称 | Dashboard | 说明 |
|---------|------|-----------|------|
| 1724 | 投放词列表 | 139 | 投放词明细数据 |
| 1726 | Campaign列表 | 139 | Campaign 列表 |
| 1731 | ROAS 7天 | 139 | 7天广告支出回报率 |
| 1732 | LTV/CAC | 139 | 生命周期价值/获客成本 |
| 1750 | ROAS 180天 | 139 | 180天广告支出回报率 |
| **4953** | **(优化版-9指标)** | - | **参考设计**: Model预处理+精简指标+双Y轴+面积图 |

### 转化分析

| Card ID | 名称 | Dashboard | 说明 |
|---------|------|-----------|------|
| 3228 | 有意向用户->支付成功 转化数据 | 254 | 转化漏斗 |
| 3267 | 有意向用户->支付成功 转化数据 - 分场景 | 254 | 分场景转化 |

### Revenue 收入分析 (Collection 521)

| Card ID | 名称 | 类型 | 说明 |
|---------|------|------|------|
| 6080 | Revenue发票数据基础 | Model | SQL 源表，发票数据（字符串时间字段） |
| 6081 | Revenue订阅用户数据基础 | Model | SQL 源表，订阅用户数据 |
| 6092 | Revenue账单分层指标-v5 | MBQL | 分层单数（新签、连续续约、升级、降级、召回、试用、其他、代理） |
| 6105 | Revenue每日收入分布 | MBQL | 分层收入（对应单数的收入金额） |
| 6112 | Revenue账单分层&总在约人数（去除试用代理） | SQL | UNION查询，含在约用户数 |
| 6113 | Daily Paid Revenue Amount | SQL | 总收入、新签收入、续约收入 |
| 6114 | Daily Paid Revenue Users | SQL | 总付费用户数、新签用户数、续约用户数 |
| 6116 | Daily Paid Revenue Full | SQL | 金额+用户数+客单价完整版 |
| **6122** | **[Model] Revenue发票数据基础(Date类型)** | Model | **带 date 类型时间字段（pay_success_time）** |
| **6123** | **[MBQL] Revenue账单分层指标(筛选器版)** | MBQL | **使用 date 类型 breakout，可关联 Dashboard 筛选器** |

**关联 Dashboard**: 494 - Revenue用户分层（新）- 迁移

---

## 按 Collection 分类

### Collection 396: COOHOM折扣体系

| Card ID | 名称 |
|---------|------|
| 3228 | 有意向用户->支付成功 转化数据 |
| 3267 | 有意向用户->支付成功 转化数据 - 分场景 |

### Collection 521: Revenue

| Card ID | 名称 |
|---------|------|
| 6080 | Revenue发票数据基础 (Model) |
| 6081 | Revenue订阅用户数据基础 (Model) |
| 6092 | Revenue账单分层指标-v5 |
| 6105 | Revenue每日收入分布 |
| 6112 | Revenue账单分层&总在约人数（去除试用代理） |
| 6113 | Daily Paid Revenue Amount |
| 6114 | Daily Paid Revenue Users |
| 6116 | Daily Paid Revenue Full |
| 6122 | Revenue发票数据基础(Date类型) (Model) |
| 6123 | Revenue账单分层指标(筛选器版) |

---

## 最佳实践案例

### Card 4953 - 优化的投放分析 Question

**设计特点:**
- ✅ **9个指标**: 合理分布在聚合和表达式中
- ✅ **Model预处理**: 时间字段在Model层处理
- ✅ **可视化参考700**: 5个核心指标显示+双Y轴+面积图

**技术要点:**
1. 条件聚合使用 `case` 而非 `if`
2. 转化率在 aggregation 中用 `/` 计算
3. 时间字段使用 Model 预处理的字段
4. 可视化: 精简指标 + 双Y轴设计

**查询方式:**
```bash
python3 ~/.claude/skills/kmb-metabase/scripts/query_card.py 4953 --output table
```

### Collection 521 迁移案例 - Revenue 用户分层

**迁移自**: Tesseract page/55074

**关键发现**: Dashboard 筛选器关联需要 **date 类型**时间字段！

| 问题 | 原因 | 解决 |
|------|------|------|
| Dashboard 筛选器无法关联 | Question breakout 使用字符串类型字段 `pay_success_day` | 创建 Model 6122 提供 `pay_success_time` (date 类型) |

**迁移策略**:
- **MBQL 适用**: 6092, 6105 - 字段都在 Model 6080 中，直接用 `case` 聚合
- **原生 SQL 适用**: 6112, 6113, 6114, 6116 - 包含 Model 没有的字段（order_type_user、UNION子查询）
- **筛选器版 MBQL**: 6123 - 使用 Model 6122 的 date 类型字段

**Model 6122 提供的时间字段**:
```sql
STR_TO_DATE(pay_success_day, '%Y%m%d') AS pay_success_time  -- date 类型
```

**MBQL case 表达式要点**:
```python
# 正确格式
def make_agg_with_and(name, filter_proxy, filter_level):
    cond1 = ["=", ["field", "is_proxy", {"base-type": "type/Integer"}], filter_proxy]
    cond2 = ["=", ["field", "member_level", {"base-type": "type/Text"}], filter_level]
    and_cond = ["and", cond1, cond2]
    inner_case = [and_cond, result]
    case_expr = ["case", [inner_case]]  # 注意：不是 [[inner_case]]
    return ["aggregation-options", ["sum", case_expr], {"name": name}]
```

**参考文档**: `references/mbql-best-practices.md` 第0节（数仓表类型）和第1节（MBQL case）

---

*最后更新: 2026-03-25*
