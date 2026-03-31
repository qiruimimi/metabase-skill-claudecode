select
        case '日'
                when '日' then created_day
                when '周' then date_format(date_trunc('week', created_day), '%Y%m%d')
                when '月' then date_format(date_trunc('month', created_day), '%Y%m%d')
                else null
            end as "时段日期"
    ,   version as "弹窗版本"
    ,   count(distinct if(open_paymentmodal_time is not null, created_time, null)) as "打开支付弹窗PV"
    ,   count(distinct if(open_paymentmodal_time is not null, userid, null)) as "打开支付弹窗UV"
    ,   count(distinct if(click_paynow_time is not null, userid, null)) as "点击PayNow UV"
    ,   count(distinct if(create_paylink_time is not null, userid, null)) as "创建Paylink UV"
    ,   count(distinct if(pay_time is not null, userid, null)) as "支付成功UV"
    ,   round(sum(if(rnk_desc = 1, amount, 0)), 1) as "支付金额"
    ,   if(count(distinct if(open_paymentmodal_time is not null, userid, null)) = 0, 0
            , count(distinct if(click_paynow_time is not null, userid, null)) * 1.00 / count(distinct if(open_paymentmodal_time is not null, userid, null))) as "打开支付弹窗->点击PayNow转化率"
    ,   if(count(distinct if(click_paynow_time is not null, userid, null)) = 0, 0
            , count(distinct if(create_paylink_time is not null, userid, null)) * 1.00 / count(distinct if(click_paynow_time is not null, userid, null))) as "点击PayNow->创建Paylink转化率"
    ,   if(count(distinct if(create_paylink_time is not null, userid, null)) = 0, 0
            , count(distinct if(pay_time is not null, userid, null)) * 1.00 / count(distinct if(create_paylink_time is not null, userid, null))) as "创建Paylink->支付成功转化率"
    ,   if(count(distinct if(create_paylink_time is not null, userid, null)) = 0, 0
            , count(distinct if(pay_time is not null, userid, null)) * 1.00 / count(distinct userid)) as "进入支付弹窗总支付成功转化率"
from (
  select
      t.*,
      case when is_coohom_paid is null or is_coohom_paid = 0 then '未付费'
           when is_coohom_paid = 1 and coohom_user_level <> 'Basic' then '付费(在约)'
           when is_coohom_paid = 1 and coohom_user_level = 'Basic' then '断约用户'
      end as user_paid_level
  from (
              select
              open._time as created_time
          ,   open.ds as created_day
          ,   open._ip
          ,   open.qhdi
          ,   open.userid
          ,   open.openposition
          ,   open._time as open_paymentmodal_time
          ,   open.version as version
          ,   click.trackerid
          ,   click.click_paynow_time
          ,   clk.create_paylink_time
          ,   pay._time as pay_time
          ,   pay.sessionid
          ,   pay.subscriptionid
          ,   pay.webhook_type
          ,   pay.invoiceid
          ,   inc.invoice_stat_plan_name
          ,   coalesce(inc.amount, 0) as amount
          ,   open._ua as ua
          ,   row_number() over(partition by invoiceid order by amount desc) as rnk_desc
      from
          (   -- **打开支付页面（建立单次弹窗打开的归因窗口）**
              select
                      _time
                  ,   ds
                  ,   _ip
                  ,   qhdi
                  ,   userid
                  ,   openposition
                  ,   _ua
                  ,   if(version is null, 'v1', version) as version
                  ,   coalesce(plantype, type) as type
                  ,   case when coalesce(plantype, type) is not null then coalesce(`interval`, 'MONTH') end as `interval`
                  ,   case when coalesce(plantype, type) is not null then coalesce(mode, 'CYCLICAL') end as mode
                  ,   lead(_time, 1, '9999-12-31 23:59:59') over(partition by userid, openposition order by _time) as next_time
              from kdw_log.dwd_log_coohom_paymentModal_opened
              where ds between '20260216' and '20260301'
              and userid is not null and userid <> ''
          ) open

      left join
          (  -- **点击支付方式（细化维度 + 跨日窗口）**
              select
                      userid
                  ,   trackerid, openposition, paysource, skuid, type, mode, `interval`
                  ,   max(ds) as ds
                  ,   max(_time) as click_paynow_time
              from kdw_log.dwd_log_coohom_payment_intentToPay
              where ds between '20260216' and '20260301'
              group by userid, trackerid, openposition, paysource, skuid, type, mode, `interval`
          ) click
      on open.userid = click.userid
      and click.ds between open.ds and date_format(str_to_date(open.ds, '%Y%m%d') + interval 1 day, '%Y%m%d')
      and open._time <= click.click_paynow_time
      and open.next_time >= click.click_paynow_time
      and open.openposition = click.openposition

      left join
          (-- **创建支付链接（沿用跨日窗口）**
              select
                      userid
                  ,   trackerid
                  ,   sessionid
                  ,   max(_time) as create_paylink_time
                  ,   max(ds) as ds
              from kdw_log.dwd_log_coohom_payment_checkout_create
              where ds between '20260216' and '20260301'
              and trackerid is not null
              group by userid, trackerid, sessionid
          ) clk
      on click.userid = clk.userid
      and clk.ds between click.ds and date_format(str_to_date(click.ds, '%Y%m%d') + interval 1 day, '%Y%m%d')
      and click.trackerid = clk.trackerid

      left join
          (-- **返回支付结果（取每 session 最早事件 + 跨日窗口）**
              select
                      userid
                  ,   ds
                  ,   _time
                  ,   sessionid
                  ,   subscriptionid
                  ,   webhook_type
                  ,   invoiceid
              from (
                      select
                              userid
                          ,   _time
                          ,   ds
                          ,   sessionid
                          ,   subscriptionid
                          ,   webhook_type
                          ,   invoiceid
                          ,   row_number() over(partition by sessionid order by _time) as rnk
                      from kdw_log.dwd_log_coohom_payment_webhook
                      where ds between '20260216' and date_format(str_to_date('20260301', '%Y%m%d') + interval 1 day, '%Y%m%d')
                      and sessionid is not null
                      and invoiceid is not null
                  ) tmp
              where rnk = 1
          ) pay
      on clk.sessionid = pay.sessionid
      and pay.ds between clk.ds and date_format(str_to_date(clk.ds, '%Y%m%d') + interval 1 day, '%Y%m%d')

      left join
          ( -- **获取成交收入（新收入口径与字段）**
              select
                      invoice_token
                  ,   sku as invoice_stat_plan_name
                  ,   coalesce(amt_usd, 0) as amount
              from hive_prod.kdw_dw.dws_coohom_trd_daily_toc_invoice_s_d
              where ds = '20260301'
              and pay_success_day between '20260216' and '20260301'
              and coalesce(amt_usd, 0) > 0
          ) inc
      on pay.invoiceid = inc.invoice_token

    ) t
  left join (
      select
          ds,
          kujiale_user_id,
          is_coohom_paid,
          coohom_user_level
      from hive_prod.exabrain.dwb_usr_coohom_user_s_d
      where ds between date_format(str_to_date('20260216', '%Y%m%d') - interval 1 day, '%Y%m%d') and date_format(str_to_date('20260301', '%Y%m%d') - interval 1 day, '%Y%m%d')
  ) last_day_u
  on t.userid = last_day_u.kujiale_user_id
  and t.created_day = date_format(str_to_date(last_day_u.ds, '%Y%m%d') + interval 1 day, '%Y%m%d')
  left join (
      select
          kujiale_user_id,
          created_day,
          created_week,
          coohom_register_country_en,
          coohom_register_country_sc
      from hive_prod.exabrain.dwb_usr_coohom_user_s_d
      where ds = '20260301'
  ) u
  on t.userid = u.kujiale_user_id
  left join (
      select
          userid kujiale_user_id,
          trackerid,
          paysource,
          type,
          mode,
          `interval`
      from hive_prod.kdw_log.dwd_log_coohom_payment_intentToPay
      where ds between '20260216' and '20260301'
  ) tracker
  on t.userid = tracker.kujiale_user_id and t.trackerid = tracker.trackerid


  where 1 = 1
  and if(array_length([]) > 0, array_contains([], openposition), true)
  and if(length('')=0, true, openposition = '')
  and if(length('')=0, true, userid = '')
  and if(length('v1')=0, true, version = 'v1')
  and if(array_length([]) > 0, array_contains([], u.coohom_register_country_sc), true)
  and if(array_length([]) > 0, array_contains([], u.coohom_register_country_en), true)
  and if(array_length([]) > 0, array_contains([], tracker.paysource), true)
  and if(length('') > 0,  if('' = '是', t.created_day = u.created_day, true), true)
  and if(length('') > 0,  if('' = '是', date_format(date_trunc('week', t.created_day), '%Y%m%d') = u.created_week, true), true)

) t
where 1 = 1
  and if(array_length([]) > 0, array_contains([], user_paid_level), true)
group by case '日'
                when '日' then created_day
                when '周' then date_format(date_trunc('week', created_day), '%Y%m%d')
                when '月' then date_format(date_trunc('month', created_day), '%Y%m%d')
                else null
            end, version
order by `时段日期` asc
limit 10000