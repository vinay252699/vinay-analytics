\# Amazon Ads Data Engineering Architecture



\## 1. Overview



This project demonstrates an end-to-end Amazon Advertising analytics data platform using Python, Google Cloud Platform, BigQuery, SQL, and Power BI.



The project is implemented using synthetic Amazon Ads API-style data for portfolio and demonstration purposes.



The architecture is designed to represent how the solution could be extended into a production Amazon Advertising analytics platform.



\---



\## 2. High-Level Architecture



```text

&#x20;                   Amazon Advertising API

&#x20;                            |

&#x20;                            | JSON / API

&#x20;                            v

&#x20;                   +-------------------+

&#x20;                   | Python Ingestion  |

&#x20;                   |   API Connector   |

&#x20;                   +---------+---------+

&#x20;                             |

&#x20;                             v

&#x20;                   +-------------------+

&#x20;                   |   GCS Raw Layer   |

&#x20;                   | Immutable JSON    |

&#x20;                   +---------+---------+

&#x20;                             |

&#x20;                             v

&#x20;                   +-------------------+

&#x20;                   | BigQuery RAW      |

&#x20;                   | raw\_ads\_reports   |

&#x20;                   +---------+---------+

&#x20;                             |

&#x20;                             | SQL / JSON parsing

&#x20;                             v

&#x20;                   +-------------------+

&#x20;                   | BigQuery Transform|

&#x20;                   | campaign\_performance|

&#x20;                   +---------+---------+

&#x20;                             |

&#x20;                             | KPI calculations

&#x20;                             v

&#x20;                   +-------------------+

&#x20;                   | Analytics Layer   |

&#x20;                   | campaign\_analytics|

&#x20;                   | campaign\_summary  |

&#x20;                   +---------+---------+

&#x20;                             |

&#x20;                             v

&#x20;                   +-------------------+

&#x20;                   | Data Quality      |

&#x20;                   | Validation Checks |

&#x20;                   +---------+---------+

&#x20;                             |

&#x20;                             v

&#x20;                   +-------------------+

&#x20;                   |    Power BI       |

&#x20;                   | Dashboards / BI   |

&#x20;                   +-------------------+



3\. Data Flow

Step 1 — Source



The production version of the platform is designed to consume data from the Amazon Advertising API.



Typical source data includes:



Campaign information

Campaign performance

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



For this portfolio implementation, synthetic Amazon Ads API-style JSON is used.



Step 2 — Python Ingestion



Python is used as the ingestion layer.



Responsibilities include:



API authentication

OAuth token handling

API requests

Response validation

JSON processing

Logging

Error handling

Writing raw data to cloud storage

Loading data into BigQuery



The application uses Google Secret Manager for sensitive Amazon credentials.



Secrets are never stored in source code or GitHub.



Step 3 — GCS Raw Layer



Google Cloud Storage acts as the raw landing zone.



Example structure:



gs://vinay-analytics-amazon-raw/

&#x20;   amazon-ads/

&#x20;       campaigns/

&#x20;           date=YYYY-MM-DD/

&#x20;               campaigns.json

&#x20;       reports/

&#x20;           date=YYYY-MM-DD/

&#x20;               report.json



The raw layer is intended to preserve the source response with minimal transformation.



This provides:



Reprocessing capability

Auditability

Source-data preservation

Recovery from downstream transformation failures

Step 4 — BigQuery RAW Layer



Raw source data is stored in BigQuery before transformation.



Current table:



amazon\_ads.raw\_ads\_reports



The raw table contains:



Column	Purpose

ingestion\_timestamp	Time when the record was ingested

source	Source system identifier

report\_type	Amazon report type

data	Raw JSON payload



The raw JSON is retained so that downstream transformations can be recreated without requesting the source API again.



4\. Transformation Layer



The transformation layer converts nested JSON into analytics-friendly relational tables.



campaign\_performance



This table represents the normalized campaign-day grain.



Grain:



One row = One campaign + One date



Important columns include:



date

campaign\_id

campaign\_name

campaign\_type

targeting\_type

daily\_budget

currency

impressions

clicks

spend

sales

orders

units

ctr

cpc

cvr

acos

roas



The transformation uses BigQuery JSON functions such as:



JSON\_VALUE()

JSON\_QUERY\_ARRAY()

UNNEST()

SAFE\_DIVIDE()

5\. Analytics Layer



The analytics layer contains business-ready tables for reporting.



campaign\_analytics



This table contains calculated KPIs at campaign-day level.



Calculated metrics include:



CTR

CPC

CVR

ACOS

ROAS

Average Order Value

CPM



Example calculations:



CTR  = Clicks / Impressions



CPC  = Spend / Clicks



CVR  = Orders / Clicks



ACOS = Spend / Sales



ROAS = Sales / Spend



AOV  = Sales / Orders



CPM  = Spend / Impressions \* 1000



SAFE\_DIVIDE() is used to prevent divide-by-zero errors.



campaign\_summary



This table aggregates campaign performance across the reporting period.



Grain:



One row = One campaign



Example metrics:



Total Impressions

Total Clicks

Total Spend

Total Sales

Total Orders

Total Units

CTR

CPC

CVR

ACOS

ROAS

Average Order Value



This table is designed for executive-level Power BI reporting.



6\. Data Quality Layer



Data quality checks are executed against the transformed data.



Current checks include:



Null validation



Check for missing values in important fields:



campaign\_id

date

impressions

clicks

spend

sales

Duplicate validation



The expected business key is:



date + campaign\_id



Duplicate records are flagged.



Business rule validation



Examples:



clicks <= impressions

spend >= 0

sales >= 0

orders >= 0

impressions >= 0



These checks help prevent invalid records from reaching the reporting layer.



7\. Power BI Semantic / Reporting Layer



Power BI consumes the analytics tables rather than the raw source data.



Recommended tables for reporting:



campaign\_analytics

campaign\_summary



The raw JSON table should not normally be exposed directly to business users.



Potential dashboard sections:



Executive Overview

Total Spend

Total Sales

ROAS

ACOS

Orders

Units

Campaign Performance

Campaign

Spend

Sales

ROAS

ACOS

Orders

CTR

CVR

Trend Analysis

Daily Spend

Daily Sales

Daily ROAS

Daily ACOS

Campaign Drill-down



Users can select a campaign and analyze its daily performance.



8\. Data Model



The current logical model is:



&#x20;                +----------------------+

&#x20;                | raw\_ads\_reports      |

&#x20;                |----------------------|

&#x20;                | ingestion\_timestamp  |

&#x20;                | source               |

&#x20;                | report\_type          |

&#x20;                | data (JSON)          |

&#x20;                +----------+-----------+

&#x20;                           |

&#x20;                           | JSON parsing

&#x20;                           v

&#x20;                +----------------------+

&#x20;                | campaign\_performance |

&#x20;                |----------------------|

&#x20;                | date                 |

&#x20;                | campaign\_id          |

&#x20;                | campaign\_name        |

&#x20;                | impressions          |

&#x20;                | clicks               |

&#x20;                | spend                |

&#x20;                | sales                |

&#x20;                | orders               |

&#x20;                | units                |

&#x20;                +----------+-----------+

&#x20;                           |

&#x20;               +-----------+-----------+

&#x20;               |                       |

&#x20;               v                       v

&#x20;      +------------------+    +------------------+

&#x20;      | campaign\_analytics|    | campaign\_summary |

&#x20;      |------------------|    |------------------|

&#x20;      | Daily KPIs       |    | Campaign KPIs    |

&#x20;      +------------------+    +------------------+

&#x20;               |                       |

&#x20;               +-----------+-----------+

&#x20;                           |

&#x20;                           v

&#x20;                        Power BI

9\. Security Architecture



Sensitive credentials are separated from application code.



Amazon Credentials

&#x20;       |

&#x20;       v

Google Secret Manager

&#x20;       |

&#x20;       v

Python Application

&#x20;       |

&#x20;       v

Amazon Advertising API



The following should never be committed to GitHub:



.env

Client Secret

Refresh Token

Access Token

Passwords

Private credentials



The project .gitignore excludes local environment files and generated raw/processed data.



10\. Production Architecture Extension



The current portfolio implementation uses a simplified architecture.



A production implementation could evolve into:



&#x20;                 Amazon Ads API

&#x20;                      |

&#x20;                      v

&#x20;             Cloud Run / Scheduler

&#x20;                      |

&#x20;                      v

&#x20;               Python Ingestion

&#x20;                      |

&#x20;                      v

&#x20;             Google Cloud Storage

&#x20;                 Raw / Immutable

&#x20;                      |

&#x20;                      v

&#x20;                   Pub/Sub

&#x20;                      |

&#x20;                      v

&#x20;               Dataflow / Beam

&#x20;                      |

&#x20;                      v

&#x20;                 BigQuery RAW

&#x20;                      |

&#x20;                      v

&#x20;                   dbt / SQL

&#x20;                      |

&#x20;            +---------+---------+

&#x20;            |                   |

&#x20;            v                   v

&#x20;      Transformation       Data Quality

&#x20;            |                   |

&#x20;            +---------+---------+

&#x20;                      |

&#x20;                      v

&#x20;              BigQuery Analytics

&#x20;                      |

&#x20;                      v

&#x20;                   Power BI



Potential production components:



Cloud Scheduler for scheduled ingestion

Cloud Run for API ingestion services

Pub/Sub for event-driven processing

Dataflow / Apache Beam for scalable processing

BigQuery for analytical storage

dbt for transformation management

Secret Manager for credentials

Cloud Logging and Monitoring for observability

IAM for least-privilege access

Power BI for business reporting

11\. Reliability and Recovery



A production implementation should support:



Idempotency



Repeated ingestion of the same report should not create duplicate business records.



A logical business key could be:



profile\_id

\+

report\_type

\+

date

\+

campaign\_id

Retry



Transient API and cloud failures should be retried using controlled exponential backoff.



Raw Data Preservation



Raw responses should be retained before transformation.



If a transformation fails, the data can be reprocessed without calling the Amazon API again.



Replay



Historical raw data can be replayed through the transformation pipeline after fixing transformation logic.



Monitoring



Important operational metrics include:



API success/failure

API latency

Records ingested

Records rejected

Transformation failures

Data freshness

Duplicate records

Data quality failures

BigQuery job failures

12\. Partitioning and Performance



As the dataset grows, BigQuery tables should be optimized for query performance and cost.



For large campaign performance tables:



PARTITION BY date



Possible clustering columns:



campaign\_id

campaign\_type

targeting\_type



This allows queries filtered by date and campaign to scan less data.



Example:



WHERE date BETWEEN '2026-09-01' AND '2026-09-30'

13\. Cost Optimization



The platform can control BigQuery cost through:



Partitioned tables

Clustering

Selecting only required columns

Avoiding SELECT \*

Reusing transformed analytics tables

Incremental transformations

Table expiration for temporary/demo datasets

Monitoring query bytes processed



For portfolio development, temporary table expiration is used to avoid retaining unnecessary demo data indefinitely.



14\. Environment Strategy



The solution can be separated into environments:



Development

&#x20;    |

&#x20;    v

Testing

&#x20;    |

&#x20;    v

Production



Each environment should have separate:



GCP datasets

Service accounts

Secrets

Configuration

Power BI connections



Example:



amazon\_ads\_dev

amazon\_ads\_test

amazon\_ads\_prod

15\. Project Design Principles



The architecture follows these principles:



Raw data preservation

Separation of ingestion and transformation

Layered data architecture

Reusable SQL transformations

Data quality before reporting

Secure credential management

Idempotent processing

Observability and recoverability

Cost-aware BigQuery design

Business-ready analytics tables

16\. Current Portfolio Implementation vs Production

Capability	Portfolio	Production Extension

Source	Synthetic API-style JSON	Amazon Ads API

Ingestion	Python	Cloud Run / Python

Raw storage	GCS design + local sample	GCS

Messaging	Not required	Pub/Sub

Processing	BigQuery SQL	Dataflow / dbt / SQL

Warehouse	BigQuery	BigQuery

Data Quality	SQL checks	Automated DQ framework

Scheduling	Manual execution	Cloud Scheduler / Composer

Secrets	Secret Manager	Secret Manager

Monitoring	Application logging	Cloud Monitoring + Logging

BI	Power BI	Power BI

CI/CD	GitHub	GitHub Actions / Cloud Build

17\. Portfolio Objective



This project demonstrates practical experience across:



API Integration

&#x20;     ↓

Python

&#x20;     ↓

Cloud Storage

&#x20;     ↓

BigQuery

&#x20;     ↓

SQL Transformation

&#x20;     ↓

Data Quality

&#x20;     ↓

Analytics Engineering

&#x20;     ↓

Power BI



The implementation intentionally separates the portfolio/demo implementation from the production architecture so that the project remains transparent about which components are currently implemented and which components represent the planned production extension.







