import json
from pathlib import Path

from google.cloud import storage


PROJECT_ID = "vinay-analytics-platform"
BUCKET_NAME = "vinay-analytics-amazon-raw"

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "sample"
    / "amazon_ads_sample_api.json"
)

GCS_OBJECT = (
    "amazon-ads/sample/"
    "date=2026-09-30/"
    "amazon_ads_sample_api.json"
)


def upload_to_gcs():

    print(f"Reading: {INPUT_FILE}")

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    client = storage.Client(project=PROJECT_ID)

    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(GCS_OBJECT)

    blob.upload_from_string(
        json.dumps(data, indent=2),
        content_type="application/json"
    )

    print("\nUpload successful!")
    print(f"gs://{BUCKET_NAME}/{GCS_OBJECT}")


if __name__ == "__main__":
    upload_to_gcs()