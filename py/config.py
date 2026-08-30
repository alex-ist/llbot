import json
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from google.oauth2 import service_account


load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Required environment variable {name} is not set")
    return value


@lru_cache(maxsize=1)
def google_credentials():
    raw_credentials = required_env("LINGOLINK_GOOGLE_SERVICE_ACCOUNT_JSON")
    try:
        credentials_info = json.loads(raw_credentials)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "LINGOLINK_GOOGLE_SERVICE_ACCOUNT_JSON must contain valid JSON"
        ) from exc

    credentials = service_account.Credentials.from_service_account_info(
        credentials_info
    )
    return credentials, credentials_info["project_id"]
