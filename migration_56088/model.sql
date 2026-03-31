-- Model: 【P56088】支付弹窗事件明细 (简化版)
-- 说明: 为MBQL设计的简化数据模型，保留核心维度字段
-- 原SQL复杂归因逻辑已简化，适合MBQL聚合分析
-- I表处理: 不限制ds，由Dashboard筛选器控制

SELECT
    -- 时间维度 (预计算，便于MBQL时间筛选)
    STR_TO_DATE(ds, '%Y%m%d') AS event_date,
    ds AS event_day,
    YEAR(STR_TO_DATE(ds, '%Y%m%d')) AS event_year,
    MONTH(STR_TO_DATE(ds, '%Y%m%d')) AS event_month,
    WEEK(STR_TO_DATE(ds, '%Y%m%d')) AS event_week,

    -- 用户标识
    userid,
    qhdi,

    -- 事件维度
    'open_paymentmodal' AS event_type,
    openposition,

    -- 版本维度 (预计算，便于分组)
    IF(version IS NULL, 'v1', version) AS popup_version,

    -- 付费计划维度 (预计算)
    COALESCE(plantype, type) AS plan_type,
    CASE
        WHEN COALESCE(plantype, type) IS NOT NULL
        THEN COALESCE(`interval`, 'MONTH')
    END AS plan_interval,
    CASE
        WHEN COALESCE(plantype, type) IS NOT NULL
        THEN COALESCE(mode, 'CYCLICAL')
    END AS plan_mode,

    -- 用户付费状态 (从子查询提取到Model层)
    CASE
        WHEN last_day_u.is_coohom_paid IS NULL OR last_day_u.is_coohom_paid = 0
        THEN '未付费'
        WHEN last_day_u.is_coohom_paid = 1
             AND last_day_u.coohom_user_level <> 'Basic'
        THEN '付费(在约)'
        WHEN last_day_u.is_coohom_paid = 1
             AND last_day_u.coohom_user_level = 'Basic'
        THEN '断约用户'
    END AS user_paid_level,

    -- 地域维度 (预计算)
    u.coohom_register_country_sc AS country_sc,
    u.coohom_register_country_en AS country_en,

    -- 金额指标 (预计算，避免Question层复杂计算)
    COALESCE(inc.amt_usd, 0) AS amount_usd,

    -- 布尔标记 (便于MBQL条件聚合)
    IF(open._time IS NOT NULL, 1, 0) AS has_open,

    -- 原始时间戳
    _time AS event_time,
    _ip AS user_ip

FROM kdw_log.dwd_log_coohom_paymentModal_opened open

-- 关联用户付费状态表
LEFT JOIN (
    SELECT
        ds,
        kujiale_user_id,
        is_coohom_paid,
        coohom_user_level
    FROM hive_prod.exabrain.dwb_usr_coohom_user_s_d
    WHERE ds >= '20260215'
) last_day_u
ON open.userid = last_day_u.kujiale_user_id
AND open.ds = date_format(
    str_to_date(last_day_u.ds, '%Y%m%d') + interval 1 day,
    '%Y%m%d'
)

-- 关联用户地域表
LEFT JOIN (
    SELECT
        kujiale_user_id,
        coohom_register_country_sc,
        coohom_register_country_en
    FROM hive_prod.exabrain.dwb_usr_coohom_user_s_d
    WHERE ds = '20260301'
) u ON open.userid = u.kujiale_user_id

-- 关联收入表
LEFT JOIN (
    SELECT
        invoice_token,
        amt_usd,
        pay_success_day
    FROM hive_prod.kdw_dw.dws_coohom_trd_daily_toc_invoice_s_d
    WHERE ds >= '20260301'
    AND COALESCE(amt_usd, 0) > 0
) inc ON open.invoiceid = inc.invoice_token

WHERE open.userid IS NOT NULL
  AND open.userid <> ''
  -- I表不限制ds，由Dashboard筛选器控制
