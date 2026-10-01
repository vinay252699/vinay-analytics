\# Amazon Advertising Data Engineering \& Analytics Pipeline



\## Overview



A portfolio project demonstrating an end-to-end data engineering pipeline for Amazon Advertising analytics.



The solution is designed around a production-style architecture:



Amazon Ads API

→ Python ingestion

→ Cloud Storage

→ BigQuery RAW

→ BigQuery Transform

→ Analytics Layer

→ Power BI



For this portfolio demonstration, synthetic Amazon Ads API-style data is used so that the project can be reproduced without access to a live advertiser account.



> The included data is synthetic/demo data and is not real Amazon advertiser data.



\## Architecture



```text

Amazon Ads API / Sample API Payload

&#x20;               |

&#x20;               v

&#x20;       Python Ingestion

&#x20;               |

&#x20;               v

&#x20;       Google Cloud Storage

&#x20;            RAW Layer

&#x20;               |

&#x20;               v

&#x20;           BigQuery

&#x20;               |

&#x20;       +-------+-------+

&#x20;       |               |

&#x20;       v               v

&#x20;  RAW Reports     Transformation

&#x20;                       |

&#x20;                       v

&#x20;                Campaign Analytics

&#x20;                       |

&#x20;                       v

&#x20;                 Campaign Summary

&#x20;                       |

&#x20;                       v

&#x20;                    Power BI



Technology Stack

Python

Google Cloud Platform

Google Cloud Storage

BigQuery

SQL

Power BI

Docker

Git / GitHub

Data Engineering Layers

1\. RAW Layer



The complete source payload is preserved in BigQuery:



amazon\_ads.raw\_ads\_reports



The raw JSON is retained to support traceability and reprocessing.



2\. Transformation Layer



The JSON report is parsed using BigQuery JSON functions and UNNEST.



Table:



amazon\_ads.campaign\_performance



Grain:



1 campaign × 1 day



3\. Data Quality



The pipeline validates:



NULL campaign IDs

NULL dates

NULL metrics

Duplicate campaign/day records

Negative spend

Negative sales

Negative orders

Negative impressions

Clicks greater than impressions

4\. Analytics Layer



Business KPIs are calculated in BigQuery:



CTR

CPC

CVR

ACOS

ROAS

Average Order Value

CPM



Tables:



amazon\_ads.campaign\_analytics



amazon\_ads.campaign\_summary



Sample Dataset



The demonstration dataset contains:



5 campaigns

30 days

150 campaign-day records

Sponsored Products campaign data

US marketplace

USD currency



Metrics include:



Impressions

Clicks

Spend

Sales

Orders

Units

CTR

CPC

CVR

ACOS

ROAS

Project Structure

amazon-ads-data-engineering/

│

├── data/

│   ├── processed/

│   ├── raw/

│   └── sample/

│       └── amazon\_ads\_sample\_api.json

│

├── src/

│   ├── app.py

│   ├── ingest\_sample.py

│   ├── load\_raw\_to\_bigquery.py

│   └── upload\_to\_gcs.py

│

├── Dockerfile

├── requirements.txt

└── README.md

Local Setup



Create a Python virtual environment:



python -m venv .venv



Activate it on Windows:



.venv\\Scripts\\activate



Install dependencies:



pip install -r requirements.txt



Run the sample ingestion:



python src/ingest\_sample.py

GCP Configuration



The project uses Google Cloud services for:



Cloud Storage

BigQuery

Secret Manager

Cloud Run



Authentication should be performed using Google Cloud Application Default Credentials or an appropriate service account.



Credentials and secrets must never be committed to GitHub.



Production Extension



The sample pipeline can be extended to a production Amazon Ads integration:



Amazon Ads API

→ OAuth

→ Scheduled ingestion

→ Cloud Run / Cloud Scheduler

→ GCS

→ BigQuery

→ Data Quality

→ Analytics

→ Power BI



Additional production capabilities can include:



Incremental ingestion

Retry handling

API rate-limit handling

Schema evolution

Partitioned BigQuery tables

Data quality monitoring

Cloud Logging

Alerting

CI/CD

Airflow / Cloud Composer orchestration

Portfolio Purpose



This project demonstrates practical experience in:



API data ingestion

Cloud data engineering

GCP architecture

BigQuery SQL

JSON processing

Data quality

Analytics engineering

BI integration

Production-oriented pipeline design

## SQL Transformation Framework

All BigQuery transformation logic is version controlled under the `sql/` directory.

### Transformation

`sql/transform/01_campaign_performance.sql`

Parses the nested Amazon Ads JSON payload using:

- `JSON_VALUE`
- `JSON_QUERY_ARRAY`
- `UNNEST`
- Explicit data type casting

The resulting table has a grain of:

**1 campaign × 1 day**

### Analytics

`sql/analytics/01_campaign_analytics.sql`

Calculates advertising KPIs including:

- CTR
- CPC
- CVR
- ACOS
- ROAS
- Average Order Value
- CPM

`sql/analytics/02_campaign_summary.sql`

Aggregates campaign performance across the reporting period.

### Data Quality

`sql/data_quality/01_data_quality_checks.sql`

Validates:

- NULL values
- Duplicate campaign/day records
- Negative metrics
- Clicks greater than impressions

## Project Structure

```text
amazon-ads-data-engineering/
│
├── data/
│   └── sample/
│       └── amazon_ads_sample_api.json
│
├── sql/
│   ├── transform/
│   │   └── 01_campaign_performance.sql
│   │
│   ├── analytics/
│   │   ├── 01_campaign_analytics.sql
│   │   └── 02_campaign_summary.sql
│   │
│   └── data_quality/
│       └── 01_data_quality_checks.sql
│
├── src/
│   ├── app.py
│   ├── ingest_sample.py
│   ├── load_raw_to_bigquery.py
│   └── upload_to_gcs.py
│
├── Dockerfile
├── requirements.txt
└── README.md