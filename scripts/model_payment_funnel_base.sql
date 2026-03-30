-- Model: 支付弹窗转化基础明细
-- 来源: 小站 page/57302 queryId 32614/32615/32617
-- 描述: 支付漏斗全流程明细数据，包含打开弹窗→点击PayNow→创建Paylink→支付成功的完整链路

WITH opened AS (
    -- 打开支付页面
    SELECT
        _time,
        ds AS created_day,
        _ip,
        qhdi,
        userid,
        openposition,
        _ua,
        IF(version IS NULL, 'v1', version) AS version,
        COALESCE(plantype, type) AS plan_type,
        CASE WHEN COALESCE(plantype, type) IS NOT NULL THEN COALESCE(`interval`, 'MONTH') END AS billing_interval,
        CASE WHEN COALESCE(plantype, type) IS NOT NULL THEN COALESCE(mode, 'CYCLICAL') END AS billing_mode,
        LEAD(_time, 1, '9999-12-31 23:59:59') OVER (PARTITION BY userid, openposition ORDER BY _time) AS next_time
    FROM hive_prod.kdw_log.dwd_log_coohom_paymentModal_opened
    WHERE userid IS NOT NULL AND userid <> ''
),
click_paynow AS (
    -- 点击支付方式
    SELECT
        userid,
        trackerid,
        openposition,
        paysource,
        skuid,
        type,
        mode,
        `interval`,
        MAX(ds) AS ds,
        MAX(_time) AS click_paynow_time
    FROM hive_prod.kdw_log.dwd_log_coohom_payment_intentToPay
    GROUP BY userid, trackerid, openposition, paysource, skuid, type, mode, `interval`
),
create_paylink AS (
    -- 创建支付链接
    SELECT
        userid,
        trackerid,
        sessionid,
        MAX(_time) AS create_paylink_time,
        MAX(ds) AS ds
    FROM hive_prod.kdw_log.dwd_log_coohom_payment_checkout_create
    WHERE trackerid IS NOT NULL
    GROUP BY userid, trackerid, sessionid
),
pay_success AS (
    -- 返回支付结果
    SELECT
        userid,
        ds,
        _time AS pay_time,
        sessionid,
        subscriptionid,
        webhook_type,
        invoiceid
    FROM (
        SELECT
            userid,
            _time,
            ds,
            sessionid,
            subscriptionid,
            webhook_type,
            invoiceid,
            ROW_NUMBER() OVER (PARTITION BY sessionid ORDER BY _time) AS rnk
        FROM hive_prod.kdw_log.dwd_log_coohom_payment_webhook
        WHERE sessionid IS NOT NULL AND invoiceid IS NOT NULL
    ) tmp
    WHERE rnk = 1
),
invoice_info AS (
    -- 获取成交收入
    SELECT
        invoice_token,
        sku AS invoice_stat_plan_name,
        COALESCE(amt_usd, 0) AS amount,
        country_chs,
        country
    FROM hive_prod.kdw_dw.dws_coohom_trd_daily_toc_invoice_s_d
    WHERE COALESCE(amt_usd, 0) > 0
),
user_last_day AS (
    -- 用户付费状态(昨日快照)
    SELECT
        ds,
        kujiale_user_id,
        is_coohom_paid,
        coohom_user_level
    FROM hive_prod.exabrain.dwb_usr_coohom_user_s_d
),
user_info AS (
    -- 用户信息
    SELECT
        kujiale_user_id,
        created_day AS user_created_day,
        created_week AS user_created_week,
        coohom_register_country_en,
        coohom_register_country_sc
    FROM hive_prod.exabrain.dwb_usr_coohom_user_s_d
),
tracker_info AS (
    -- 追踪器信息
    SELECT
        userid AS kujiale_user_id,
        trackerid,
        paysource,
        type,
        mode,
        `interval`
    FROM hive_prod.kdw_log.dwd_log_coohom_payment_intentToPay
)

-- 主查询: 支付漏斗关联
SELECT
    open._time AS created_time,
    open.created_day,
    open._ip,
    open.qhdi,
    open.userid,
    open.openposition,
    open._time AS open_paymentmodal_time,
    open.version,
    open.plan_type,
    open.billing_interval,
    open.billing_mode,
    click.trackerid,
    click.click_paynow_time,
    clk.create_paylink_time,
    pay.pay_time,
    pay.sessionid,
    pay.subscriptionid,
    pay.webhook_type,
    pay.invoiceid,
    inc.invoice_stat_plan_name,
    COALESCE(inc.amount, 0) AS amount,
    inc.country_chs,
    inc.country,
    open._ua AS ua,
    ROW_NUMBER() OVER (PARTITION BY pay.invoiceid ORDER BY COALESCE(inc.amount, 0) DESC) AS rnk_desc,
    -- 用户付费级别
    CASE
        WHEN last_day_u.is_coohom_paid IS NULL OR last_day_u.is_coohom_paid = 0 THEN '未付费'
        WHEN last_day_u.is_coohom_paid = 1 AND last_day_u.coohom_user_level <> 'Basic' THEN '付费(在约)'
        WHEN last_day_u.is_coohom_paid = 1 AND last_day_u.coohom_user_level = 'Basic' THEN '断约用户'
    END AS user_paid_level,
    -- 国家信息
    COALESCE(inc.country, u.coohom_register_country_en) AS country_en,
    COALESCE(inc.country_chs, u.coohom_register_country_sc) AS country_sc,
    -- 追踪器信息
    tracker.paysource,
    tracker.type AS tracker_type,
    tracker.mode AS tracker_mode,
    tracker.interval AS tracker_interval
FROM opened open
LEFT JOIN click_paynow click
    ON open.userid = click.userid
    AND click.ds BETWEEN open.created_day AND DATE_FORMAT(STR_TO_DATE(open.created_day, '%Y%m%d') + INTERVAL 1 DAY, '%Y%m%d')
    AND open._time <= click.click_paynow_time
    AND open.next_time >= click.click_paynow_time
    AND open.openposition = click.openposition
LEFT JOIN create_paylink clk
    ON click.userid = clk.userid
    AND clk.ds BETWEEN click.ds AND DATE_FORMAT(STR_TO_DATE(click.ds, '%Y%m%d') + INTERVAL 1 DAY, '%Y%m%d')
    AND click.trackerid = clk.trackerid
LEFT JOIN pay_success pay
    ON clk.sessionid = pay.sessionid
    AND pay.ds BETWEEN clk.ds AND DATE_FORMAT(STR_TO_DATE(clk.ds, '%Y%m%d') + INTERVAL 1 DAY, '%Y%m%d')
LEFT JOIN invoice_info inc
    ON pay.invoiceid = inc.invoice_token
LEFT JOIN user_last_day last_day_u
    ON open.userid = last_day_u.kujiale_user_id
    AND open.created_day = DATE_FORMAT(STR_TO_DATE(last_day_u.ds, '%Y%m%d') + INTERVAL 1 DAY, '%Y%m%d')
LEFT JOIN user_info u
    ON open.userid = u.kujiale_user_id
LEFT JOIN tracker_info tracker
    ON open.userid = tracker.kujiale_user_id
    AND click.trackerid = tracker.trackerid
