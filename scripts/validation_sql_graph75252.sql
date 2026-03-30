-- 小站SQL简化验证版本 (graphId=75252)
-- 用于对比KMB MBQL Question的数据一致性

SELECT
    created_day AS "时段日期",
    COUNT(DISTINCT IF(open_paymentmodal_time IS NOT NULL, created_time, NULL)) AS "打开支付弹窗PV",
    COUNT(DISTINCT IF(open_paymentmodal_time IS NOT NULL, userid, NULL)) AS "打开支付弹窗UV",
    COUNT(DISTINCT IF(click_paynow_time IS NOT NULL, userid, NULL)) AS "点击PayNow UV",
    COUNT(DISTINCT IF(create_paylink_time IS NOT NULL, userid, NULL)) AS "创建Paylink UV",
    COUNT(DISTINCT IF(pay_time IS NOT NULL, userid, NULL)) AS "支付成功UV",
    ROUND(SUM(IF(rnk_desc = 1, amount, 0)), 1) AS "支付金额"
FROM (
    SELECT
        open._time AS created_time,
        open.ds AS created_day,
        open.qhdi,
        open.userid,
        open._time AS open_paymentmodal_time,
        click.click_paynow_time,
        clk.create_paylink_time,
        pay._time AS pay_time,
        inc.amount,
        ROW_NUMBER() OVER (PARTITION BY pay.invoiceid ORDER BY COALESCE(inc.amount, 0) DESC) AS rnk_desc
    FROM (
        SELECT _time, ds, qhdi, userid, openposition, _ua,
            LEAD(_time, 1, '9999-12-31 23:59:59') OVER (PARTITION BY userid, openposition ORDER BY _time) AS next_time
        FROM hive_prod.kdw_log.dwd_log_coohom_paymentModal_opened
        WHERE ds >= DATE_FORMAT(DATE_SUB(CURRENT_DATE, 30), '%Y%m%d')
        AND userid IS NOT NULL AND userid <> ''
    ) open
    LEFT JOIN (
        SELECT userid, trackerid, openposition, paysource, MAX(ds) AS ds, MAX(_time) AS click_paynow_time
        FROM hive_prod.kdw_log.dwd_log_coohom_payment_intentToPay
        WHERE ds >= DATE_FORMAT(DATE_SUB(CURRENT_DATE, 30), '%Y%m%d')
        GROUP BY userid, trackerid, openposition, paysource
    ) click ON open.userid = click.userid
        AND click.ds BETWEEN open.ds AND DATE_FORMAT(STR_TO_DATE(open.ds, '%Y%m%d') + INTERVAL 1 DAY, '%Y%m%d')
        AND open._time <= click.click_paynow_time
        AND open.next_time >= click.click_paynow_time
        AND open.openposition = click.openposition
    LEFT JOIN (
        SELECT userid, trackerid, sessionid, MAX(_time) AS create_paylink_time, MAX(ds) AS ds
        FROM hive_prod.kdw_log.dwd_log_coohom_payment_checkout_create
        WHERE ds >= DATE_FORMAT(DATE_SUB(CURRENT_DATE, 30), '%Y%m%d')
        AND trackerid IS NOT NULL
        GROUP BY userid, trackerid, sessionid
    ) clk ON click.userid = clk.userid
        AND clk.ds BETWEEN click.ds AND DATE_FORMAT(STR_TO_DATE(click.ds, '%Y%m%d') + INTERVAL 1 DAY, '%Y%m%d')
        AND click.trackerid = clk.trackerid
    LEFT JOIN (
        SELECT userid, ds, _time, sessionid, invoiceid
        FROM (
            SELECT userid, _time, ds, sessionid, invoiceid,
                ROW_NUMBER() OVER (PARTITION BY sessionid ORDER BY _time) AS rnk
            FROM hive_prod.kdw_log.dwd_log_coohom_payment_webhook
            WHERE ds >= DATE_FORMAT(DATE_SUB(CURRENT_DATE, 30), '%Y%m%d')
            AND sessionid IS NOT NULL AND invoiceid IS NOT NULL
        ) tmp WHERE rnk = 1
    ) pay ON clk.sessionid = pay.sessionid
        AND pay.ds BETWEEN clk.ds AND DATE_FORMAT(STR_TO_DATE(clk.ds, '%Y%m%d') + INTERVAL 1 DAY, '%Y%m%d')
    LEFT JOIN (
        SELECT invoice_token, COALESCE(amt_usd, 0) AS amount
        FROM hive_prod.kdw_dw.dws_coohom_trd_daily_toc_invoice_s_d
        WHERE ds = DATE_FORMAT(DATE_SUB(CURRENT_DATE, 1), '%Y%m%d')
        AND COALESCE(amt_usd, 0) > 0
    ) inc ON pay.invoiceid = inc.invoice_token
) t
GROUP BY created_day
ORDER BY created_day DESC
LIMIT 10