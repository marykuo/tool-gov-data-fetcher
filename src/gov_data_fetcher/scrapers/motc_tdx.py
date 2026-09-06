import os
import requests
from dotenv import load_dotenv

# 載入定義在 .env 檔案中的環境變數
load_dotenv()
CLIENT_ID = os.getenv("MOTC_TDX_CLIENT_ID")
CLIENT_SECRET = os.getenv("MOTC_TDX_CLIENT_SECRET")

MOTC_TDX_HOST = "https://tdx.transportdata.tw"


def fetch_motc_tdx_rail_data():
    """Fetch and save rail data for all TDX rail systems."""
    access_token = get_motc_tdx_access_token()


def get_motc_tdx_access_token(host: str = MOTC_TDX_HOST) -> str:
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError("MOTC_TDX_CLIENT_ID and MOTC_TDX_CLIENT_SECRET must be set")

    response = requests.post(
        f"{host}/auth/realms/TDXConnect/protocol/openid-connect/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    )
    response.raise_for_status()
    json = response.json()
    token = json.get("access_token")
    if not token:
        raise ValueError("TDX token response did not contain access_token")
    print(
        f"Obtained TDX access token: {token[:10]}..., expires in {json.get('expires_in')} seconds"
    )
    return token
