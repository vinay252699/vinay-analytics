import json
import os
from datetime import datetime, timezone

import requests
from flask import Flask, request, jsonify
from google.cloud import secretmanager, storage, bigquery

app = Flask(__name__)

PROJECT_ID = os.environ.get(
    "GOOGLE_CLOUD_PROJECT",
    "vinay-analytics-platform"
)

CLIENT_ID = os.environ.get("AMAZON_LWA_CLIENT_ID")

CLIENT_SECRET_NAME = "amazon-ads-client-secret"
REFRESH_TOKEN_SECRET_NAME = "amazon-ads-refresh-token"

GCS_BUCKET_NAME = "vinay-analytics-amazon-raw"
BQ_DATASET = "amazon_ads"
BQ_TABLE = "raw_campaigns"
US_PROFILE_ID = "1551266973959403"

REDIRECT_URI = (
    "https://vinay-amazon-ads-oauth-623477488653.us-east1.run.app"
    "/amazon/callback"
)

TOKEN_URL = "https://api.amazon.com/auth/o2/token"
CAMPAIGNS_URL = (
    "https://advertising-api.amazon.com/sp/campaigns/list"
)


# ---------------------------------------------------------
# Secret Manager
# ---------------------------------------------------------

def get_client_secret():
    client = secretmanager.SecretManagerServiceClient()

    secret_path = (
        f"projects/{PROJECT_ID}/secrets/"
        f"{CLIENT_SECRET_NAME}/versions/latest"
    )

    response = client.access_secret_version(
        request={"name": secret_path}
    )

    return response.payload.data.decode("UTF-8")


def get_refresh_token():
    client = secretmanager.SecretManagerServiceClient()

    secret_path = (
        f"projects/{PROJECT_ID}/secrets/"
        f"{REFRESH_TOKEN_SECRET_NAME}/versions/latest"
    )

    response = client.access_secret_version(
        request={"name": secret_path}
    )

    return response.payload.data.decode("UTF-8")


def save_refresh_token(refresh_token):
    client = secretmanager.SecretManagerServiceClient()

    secret_path = (
        f"projects/{PROJECT_ID}/secrets/"
        f"{REFRESH_TOKEN_SECRET_NAME}"
    )

    client.add_secret_version(
        request={
            "parent": secret_path,
            "payload": {
                "data": refresh_token.encode("UTF-8")
            },
        }
    )


# ---------------------------------------------------------
# Amazon Access Token
# ---------------------------------------------------------

def get_access_token():
    client_secret = get_client_secret()
    refresh_token = get_refresh_token()

    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID,
            "client_secret": client_secret,
        },
        timeout=30,
    )

    if response.status_code != 200:
        app.logger.error(
            "Amazon access token refresh failed: HTTP %s",
            response.status_code,
        )
        return None

    token_data = response.json()

    # Amazon may return a new refresh token.
    # Save it so the latest token is always available.
    new_refresh_token = token_data.get("refresh_token")

    if new_refresh_token:
        save_refresh_token(new_refresh_token)
        app.logger.info("Amazon refresh token rotated successfully.")

    return token_data.get("access_token")


# ---------------------------------------------------------
# GCS
# ---------------------------------------------------------

def save_to_gcs(data, object_name):
    client = storage.Client(project=PROJECT_ID)

    bucket = client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(object_name)

    blob.upload_from_string(
        json.dumps(data, indent=2),
        content_type="application/json",
    )

    app.logger.info(
        "Saved Amazon Ads data to gs://%s/%s",
        GCS_BUCKET_NAME,
        object_name,
    )

def save_to_bigquery(data):
    client = bigquery.Client(project=PROJECT_ID)

    table_id = f"{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}"

    rows = [
        {
            "ingestion_timestamp": datetime.now(timezone.utc).isoformat(),
            "profile_id": US_PROFILE_ID,
            "source": "amazon_ads_api",
            "data": json.dumps(data),
        }
    ]

    errors = client.insert_rows_json(
        table_id,
        rows,
    )

    if errors:
        app.logger.error(
            "BigQuery insert failed: %s",
            errors,
        )
        raise RuntimeError("BigQuery insert failed")

    app.logger.info(
        "Saved Amazon Ads data to BigQuery: %s",
        table_id,
    )
# ---------------------------------------------------------
# Home
# ---------------------------------------------------------

@app.route("/")
def home():
    return "Vinay Analytics Amazon Ads API - OAuth Server"


# ---------------------------------------------------------
# Amazon OAuth Callback
# ---------------------------------------------------------

@app.route("/amazon/callback")
def amazon_callback():

    code = request.args.get("code")
    error = request.args.get("error")

    if error:
        return f"Amazon authorization failed: {error}", 400

    if not code:
        return "No authorization code received.", 400

    try:
        client_secret = get_client_secret()

        response = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": CLIENT_ID,
                "client_secret": client_secret,
                "redirect_uri": REDIRECT_URI,
            },
            timeout=30,
        )

        if response.status_code != 200:
            app.logger.error(
                "Amazon token exchange failed: HTTP %s",
                response.status_code,
            )
            return "Amazon token exchange failed.", 500

        token_data = response.json()

        refresh_token = token_data.get("refresh_token")

        if not refresh_token:
            app.logger.error(
                "Amazon did not return a refresh token."
            )
            return "Amazon did not return a refresh token.", 500

        save_refresh_token(refresh_token)

        app.logger.info(
            "Amazon authorization completed successfully."
        )

        return (
            "Amazon authorization successful. "
            "Refresh token has been stored securely. "
            "You can close this browser window."
        )

    except Exception:
        app.logger.exception("OAuth processing failed.")
        return "OAuth processing failed.", 500


# ---------------------------------------------------------
# Amazon Profiles
# ---------------------------------------------------------

@app.route("/amazon/profiles")
def amazon_profiles():

    try:
        access_token = get_access_token()

        if not access_token:
            return "Unable to obtain Amazon access token.", 500

        response = requests.get(
            "https://advertising-api.amazon.com/v2/profiles",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Amazon-Advertising-API-ClientId": CLIENT_ID,
            },
            timeout=30,
        )

        if response.status_code != 200:
            app.logger.error(
                "Amazon Profiles API failed: HTTP %s",
                response.status_code,
            )
            return "Amazon Profiles API request failed.", 500

        return jsonify(response.json())

    except Exception:
        app.logger.exception("Profiles request failed.")
        return "Profiles request failed.", 500


# ---------------------------------------------------------
# Amazon Campaigns → GCS
# ---------------------------------------------------------

@app.route("/amazon/campaigns")
def amazon_campaigns():

    try:
        access_token = get_access_token()

        if not access_token:
            return "Unable to obtain Amazon access token.", 500

        response = requests.post(
            CAMPAIGNS_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Amazon-Advertising-API-ClientId": CLIENT_ID,
                "Amazon-Advertising-API-Scope": US_PROFILE_ID,
                "Accept": "application/vnd.spCampaign.v3+json",
                "Content-Type": "application/vnd.spCampaign.v3+json",
            },
            json={
                "maxResults": 100
            },
            timeout=30,
        )

        if response.status_code != 200:
            app.logger.error(
                "Amazon Campaign API failed: HTTP %s",
                response.status_code,
            )
            return "Amazon Campaign API request failed.", 500

        campaign_data = response.json()

        # Create date-based raw storage path.
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        object_name = (
            f"amazon-ads/campaigns/"
            f"date={today}/campaigns.json"
        )

        # Save raw API response to GCS.
        save_to_gcs(
            campaign_data,
            object_name,
        )

        save_to_bigquery(campaign_data)
        
        return jsonify({
            "status": "success",
            "gcs_object": f"gs://{GCS_BUCKET_NAME}/{object_name}",
            "amazon_response": campaign_data,
        })

    except Exception:
        app.logger.exception(
            "Campaign ingestion failed."
        )
        return "Campaign ingestion failed.", 500


# ---------------------------------------------------------
# Start application
# ---------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port,
    )