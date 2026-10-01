CREATE OR REPLACE TABLE
`vinay-analytics-platform.amazon_ads.campaign_summary`
OPTIONS (
  expiration_timestamp = TIMESTAMP_ADD(
    CURRENT_TIMESTAMP(),
    INTERVAL 30 DAY
  )
)
AS

SELECT
  campaign_id,
  campaign_name,
  campaign_type,
  targeting_type,
  currency,

  SUM(impressions) AS impressions,
  SUM(clicks) AS clicks,
  SUM(spend) AS spend,
  SUM(sales) AS sales,
  SUM(orders) AS orders,
  SUM(units) AS units,

  SAFE_DIVIDE(
    SUM(clicks),
    SUM(impressions)
  ) AS ctr,

  SAFE_DIVIDE(
    SUM(spend),
    SUM(clicks)
  ) AS cpc,

  SAFE_DIVIDE(
    SUM(orders),
    SUM(clicks)
  ) AS cvr,

  SAFE_DIVIDE(
    SUM(spend),
    SUM(sales)
  ) AS acos,

  SAFE_DIVIDE(
    SUM(sales),
    SUM(spend)
  ) AS roas,

  SAFE_DIVIDE(
    SUM(sales),
    SUM(orders)
  ) AS average_order_value

FROM
  `vinay-analytics-platform.amazon_ads.campaign_performance`

GROUP BY
  campaign_id,
  campaign_name,
  campaign_type,
  targeting_type,
  currency;