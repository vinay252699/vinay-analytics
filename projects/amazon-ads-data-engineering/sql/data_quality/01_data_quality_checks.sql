-- ============================================================
-- Amazon Ads Data Quality Checks
-- Grain: 1 campaign x 1 day
-- ============================================================


-- 1. NULL checks
SELECT
  COUNT(*) AS total_rows,

  COUNTIF(campaign_id IS NULL)
    AS null_campaign_id,

  COUNTIF(date IS NULL)
    AS null_date,

  COUNTIF(impressions IS NULL)
    AS null_impressions,

  COUNTIF(clicks IS NULL)
    AS null_clicks,

  COUNTIF(spend IS NULL)
    AS null_spend,

  COUNTIF(sales IS NULL)
    AS null_sales

FROM
  `vinay-analytics-platform.amazon_ads.campaign_performance`;


-- 2. Duplicate campaign/day check
SELECT
  date,
  campaign_id,
  COUNT(*) AS record_count

FROM
  `vinay-analytics-platform.amazon_ads.campaign_performance`

GROUP BY
  date,
  campaign_id

HAVING COUNT(*) > 1

ORDER BY
  record_count DESC;


-- 3. Business-rule validation
SELECT
  COUNTIF(clicks > impressions)
    AS clicks_greater_than_impressions,

  COUNTIF(spend < 0)
    AS negative_spend,

  COUNTIF(sales < 0)
    AS negative_sales,

  COUNTIF(orders < 0)
    AS negative_orders,

  COUNTIF(impressions < 0)
    AS negative_impressions

FROM
  `vinay-analytics-platform.amazon_ads.campaign_performance`;