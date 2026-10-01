CREATE OR REPLACE TABLE
`vinay-analytics-platform.amazon_ads.campaign_analytics`
OPTIONS (
  expiration_timestamp = TIMESTAMP_ADD(
    CURRENT_TIMESTAMP(),
    INTERVAL 30 DAY
  )
)
AS

SELECT
  date,
  campaign_id,
  campaign_name,
  campaign_type,
  targeting_type,
  currency,
  daily_budget,

  impressions,
  clicks,
  spend,
  sales,
  orders,
  units,

  SAFE_DIVIDE(clicks, impressions) AS ctr,

  SAFE_DIVIDE(spend, clicks) AS cpc,

  SAFE_DIVIDE(orders, clicks) AS cvr,

  SAFE_DIVIDE(spend, sales) AS acos,

  SAFE_DIVIDE(sales, spend) AS roas,

  SAFE_DIVIDE(sales, orders) AS average_order_value,

  SAFE_DIVIDE(spend, impressions) * 1000 AS cpm

FROM
  `vinay-analytics-platform.amazon_ads.campaign_performance`;