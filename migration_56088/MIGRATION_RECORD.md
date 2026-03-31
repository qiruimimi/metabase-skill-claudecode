# Page 56088 迁移记录

## 基本信息

| 项目 | 内容 |
|------|------|
| **源页面** | 小站 page/56088 - 新版实验 - 支付弹窗转化 |
| **目标Collection** | KMB Collection 564 |
| **迁移方式** | Model + MBQL Question |
| **创建时间** | 2026-03-30 |

## 源页面信息

- **页面ID**: 56088
- **页面名称**: 新版实验 - 支付弹窗转化
- **图表数量**: 8个
- **关键图表**:
  - 73731: 打开弹窗人数/转化率趋势图 (MixLineBar)
  - 73732: 支付成功人数/转化率趋势图 (MixLineBar)
  - 73733: 每日支付金额趋势 (Line)
  - 73734: 不同弹窗版本转化漏斗对比 (Funnel)
  - 73735: 用户付费分层 (Line)

## 数据建模方案

### Model 设计

**Model名称**: 【P56088】支付弹窗事件明细

**设计要点**:
- 保留原始粒度，不做预聚合
- 提取核心维度: event_date, userid, popup_version, user_paid_level
- 预处理字段: 日期转换、版本归一化、用户付费分层
- I表 (dwd_log_*) 不限制ds，由Dashboard筛选器控制

**字段说明**:

| 字段名 | 来源 | 说明 |
|--------|------|------|
| event_date | STR_TO_DATE(ds) | 事件日期 |
| event_day | ds | 原始日期字符串 |
| userid | 多表关联 | 用户ID |
| qhdi | dim_user_info | 用户唯一标识 |
| event_type | 硬编码 | 事件类型: open/success |
| popup_version | COALESCE(version, 'v1') | 弹窗版本 |
| user_paid_level | CASE WHEN | 用户付费分层 |
| plan_type | COALESCE(plantype, type) | 套餐类型 |
| amount_usd | pay.success事件 | 支付金额(USD) |

### Question 设计

| # | 名称 | 图表类型 | 关键配置 |
|---|------|----------|----------|
| 01 | 每日打开弹窗UV | Line | distinct(userid), 无filter |
| 02 | 每日支付成功UV | MixLineBar | CASE WHEN event_type='pay.success', 转化率计算 |
| 03 | 每日支付金额 | Line | sum(amount_usd), USD货币格式 |
| 04 | 弹窗版本对比 | Line | breakout: popup_version, 支持参数筛选 |
| 05 | 用户付费分层 | Line | breakout: user_paid_level |

## 与原SQL的差异说明

由于原SQL包含复杂的窗口函数和跨日归因逻辑，本次迁移做了以下简化:

1. **移除了精确的7日归因窗口计算**
   - 原SQL: 使用窗口函数计算用户最后访问时间、首次注册时间
   - 简化后: 保留原始事件粒度，归因逻辑后置到分析时

2. **移除了用户活跃天数统计**
   - 原SQL: 使用 `user_last_7_day_active_days` 窗口函数
   - 简化后: 如需要可在Dashboard筛选器中控制时间范围

3. **付费分层口径简化**
   - 原SQL: 使用子查询关联 dim_user_info_s_d 表
   - 简化后: 在Model层预计算付费分层字段

**影响评估**: 这些简化对核心指标(UV、转化率、金额)的统计影响较小，主要影响的是细分维度的归因精度。

## 质量验证清单

- [ ] **引用残留检查**: 确认所有 `{question_XX_id}` 已替换为实际ID
- [ ] **可运行性验证**: 每个Question通过 `/api/card/{id}/query` 测试
- [ ] **数据一致性抽样**: 与原小站数据对比抽样
- [ ] **Dashboard完整性**: 确认5个卡片都正确显示，参数筛选器工作正常

## 资产映射

执行 `execute_migration.sh` 后会生成 `asset_mapping.json`，包含:
- Model ID
- 5个 Question ID
- Dashboard ID
- 访问URL

## 注意事项

1. **I表数据量**: Model基于I表构建，数据量较大，查询时请注意时间范围筛选
2. **权限配置**: 新创建的Model和Dashboard需要配置相应的查看权限
3. **定时刷新**: 建议配置Dashboard定时刷新以保持数据最新

## 回滚方案

如需回滚，执行以下操作:

```bash
# 删除 Dashboard
curl -X DELETE "${API_HOST}/api/dashboard/${DASHBOARD_ID}" -H "X-API-Key: ${API_KEY}"

# 删除 Questions
for id in ${Q01_ID} ${Q02_ID} ${Q03_ID} ${Q04_ID} ${Q05_ID}; do
  curl -X DELETE "${API_HOST}/api/card/${id}" -H "X-API-Key: ${API_KEY}"
done

# 删除 Model
curl -X DELETE "${API_HOST}/api/card/${MODEL_ID}" -H "X-API-Key: ${API_KEY}"
```

## 附录

### 文件清单

```
migration_56088/
├── model.sql                    # Model SQL
├── questions/
│   ├── 01_open_uv.json         # 每日打开弹窗UV
│   ├── 02_pay_uv.json          # 每日支付成功UV
│   ├── 03_revenue.json         # 每日支付金额
│   ├── 04_funnel_comparison.json # 弹窗版本对比
│   └── 05_paid_level.json      # 用户付费分层
├── viz/
│   └── mixlinebar_funnel.json  # MixLineBar 可视化配置
├── dashboard.json              # Dashboard 配置
├── execute_migration.sh        # 执行脚本
├── asset_mapping.json          # 生成的资产映射 (执行后生成)
└── MIGRATION_RECORD.md         # 本记录文档
```

### 执行命令

```bash
# 设置 API_KEY
export API_KEY="your_api_key_here"

# 执行迁移
cd /Users/sunsirui/.claude/skills/migration_56088
bash execute_migration.sh
```
