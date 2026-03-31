-- Model: 支付弹窗事件明细 (简化版)
-- 说明: 保留核心字段，移除复杂时间窗口归因
-- I表处理: 不限制ds，由Dashboard筛选器控制

SELECT
    -- 时间字段
    STR_TO_DATE(ds, '%Y%m%d') AS event_date,
    ds AS event_day,

    -- 用户维度
    userid,
    qhdi,

    -- 事件类型标记 (从原表提取)
    'open_paymentmodal' AS event_type,
    openposition,

    -- 版本信息
    IF(version IS NULL, 'v1', version) AS popup_version,

    -- 付费计划信息
    COALESCE(plantype, type) AS plan_type,
    CASE WHEN COALESCE(plantype, type) IS NOT NULL THEN COALESCE(`interval`, 'MONTH') END AS plan_interval,
    CASE WHEN COALESCE(plantype, type) IS NOT NULL THEN COALESCE(mode, 'CYCLICAL') END AS plan_mode,

    -- 用户属性 (从用户表关联)
    u.coohom_register_country_sc AS country_sc,
    u.coohom_register_country_en AS country_en,

    -- 金额信息 (关联收入表)
    COALESCE(inc.amt_usd, 0) AS amount_usd,

    -- 时间戳
    _time AS event_time,
    _ip AS user_ip,
    _ua AS user_agent

FROM kdw_log.dwd_log_coohom_paymentModal_opened open

LEFT JOIN (
    -- 用户维度表 (取最新状态)
    SELECT
        kujiale_user_id,
        coohom_register_country_sc,
        coohom_register_country_en
    FROM hive_prod.exabrain.dwb_usr_coohom_user_s_d
    WHERE ds = '20260301'
) u ON open.userid = u.kujiale_user_id

LEFT JOIN (
    -- 收入表 (关联invoice)
    SELECT
        invoice_token,
        amt_usd
    FROM hive_prod.kdw_dw.dws_coohom_trd_daily_toc_invoice_s_d
    WHERE ds = '20260301'
    AND pay_success_day BETWEEN '20260216' AND '20260301'
    AND COALESCE(amt_usd, 0) > 0
) inc ON open.invoiceid = inc.invoice_token

WHERE open.userid IS NOT NULL
  AND open.userid <> ''
  -- I表不限制ds，由Dashboard筛选器控制时间范围
