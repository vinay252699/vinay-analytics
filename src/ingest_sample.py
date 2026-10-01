import json
from pathlib import Path
from datetime import datetime, timezone


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "sample"
    / "amazon_ads_sample_api.json"
)


def load_sample_data():
    print(f"Reading file: {INPUT_FILE}")

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data


def main():
    data = load_sample_data()

    rows = data["report"]["rows"]

    print("\nAmazon Ads Sample Data")
    print("----------------------")
    print(f"Report type : {data['report']['reportType']}")
    print(f"Date range  : {data['report']['startDate']} "
          f"to {data['report']['endDate']}")
    print(f"Records     : {len(rows)}")
    print(f"Loaded at   : {datetime.now(timezone.utc)}")

    print("\nFirst record:")
    print(json.dumps(rows[0], indent=2))


if __name__ == "__main__":
    main()