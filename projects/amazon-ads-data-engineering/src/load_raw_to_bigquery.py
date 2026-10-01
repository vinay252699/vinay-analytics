import json
from pathlib import Path
from datetime import datetime, timezone

from google.cloud import bigquery


PROJECT_ID = "vinay-analytics-platform"
DATASET_ID = "amazon_ads"
TABLE_ID = "raw_ads_reports"

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "sample"
    / "amazon_ads_sample_api.json"
)


def create_table(client):

    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    schema = [
        bigquery.SchemaField(
            "ingestion_timestamp",
            "TIMESTAMP",
            mode="REQUIRED"
        ),
        bigquery.SchemaField(
            "source",
            "STRING"
        ),
        bigquery.SchemaField(
            "report_type",
            "STRING"
        ),
        bigquery.SchemaField(
            "data",
            "STRING"
        ),
    ]

    table = bigquery.Table(table_ref, schema=schema)

    table = client.create_table(
        table,
        exists_ok=True
    )

    print(f"Table ready: {table_ref}")


def load_data(client):

    print(f"Reading: {INPUT_FILE}")

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    row = {
        "ingestion_timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "source": "synthetic_amazon_ads_api",

        "report_type": data["report"]["reportType"],

        "data": json.dumps(data),
    }

    temp_file = PROJECT_ROOT / "data" / "raw" / "raw_ads_row.json"

    temp_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        temp_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            json.dumps(row) + "\n"
        )

    print(f"Created load file: {temp_file}")

    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField(
                "ingestion_timestamp",
                "TIMESTAMP",
                mode="REQUIRED"
            ),
            bigquery.SchemaField(
                "source",
                "STRING"
            ),
            bigquery.SchemaField(
                "report_type",
                "STRING"
            ),
            bigquery.SchemaField(
                "data",
                "STRING"
            ),
        ],
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    with open(
        temp_file,
        "rb"
    ) as file:

        load_job = client.load_table_from_file(
            file,
            table_ref,
            job_config=job_config,
        )

    load_job.result()

    print("RAW data loaded successfully!")
    print(f"Loaded into: {table_ref}")


def main():

    client = bigquery.Client(
        project=PROJECT_ID
    )

    create_table(client)
    load_data(client)


if __name__ == "__main__":
    main()