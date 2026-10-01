CREATE OR REPLACE TABLE
`vinay-analytics-platform.amazon_ads.campaign_performance`
OPTIONS (
  expiration_timestamp = TIMESTAMP_ADD(
    CURRENT_TIMESTAMP(),
    INTERVAL 30 DAY
  )
)
AS

SELECT
  JSON_VALUE(row_data, '$.date') AS date,
  JSON_VALUE(row_data, '$.campaignId') AS campaign_id,
  JSON_VALUE(row_data, '$.campaignName') AS campaign_name,
  JSON_VALUE(row_data, '$.campaignType') AS campaign_type,
  JSON_VALUE(row_data, '$.targetingType') AS targeting_type,

  CAST(JSON_VALUE(row_data, '$.dailyBudget') AS FLOAT64)
    AS daily_budget,

  JSON_VALUE(row_data, '$.currency') AS currency,

  CAST(JSON_VALUE(row_data, '$.impressions') AS INT64)
    AS impressions,

  CAST(JSON_VALUE(row_data, '$.clicks') AS INT64)
    AS clicks,

  CAST(JSON_VALUE(row_data, '$.spend') AS FLOAT64)
    AS spend,

  CAST(JSON_VALUE(row_data, '$.sales') AS FLOAT64)
    AS sales,

  CAST(JSON_VALUE(row_data, '$.orders') AS INT64)
    AS orders,

  CAST(JSON_VALUE(row_data, '$.units') AS INT64)
    AS units,

  CAST(JSON_VALUE(row_data, '$.ctr') AS FLOAT64)
    AS ctr,

  CAST(JSON_VALUE(row_data, '$.cpc') AS FLOAT64)
    AS cpc,

  CAST(JSON_VALUE(row_data, '$.cvr') AS FLOAT64)
    AS cvr,

  CAST(JSON_VALUE(row_data, '$.acos') AS FLOAT64)
    AS acos,

  CAST(JSON_VALUE(row_data, '$.roas') AS FLOAT64)
    AS roas

FROM
  `vinay-analytics-platform.amazon_ads.raw_ads_reports`,
UNNEST(
  JSON_QUERY_ARRAY(data, '$.report.rows')
) AS row_data;