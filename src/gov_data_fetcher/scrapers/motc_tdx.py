import os
import time
import requests
from dotenv import load_dotenv
from pathlib import Path
from gov_data_fetcher.core.utility import (
    fetch_api,
    save_json_to_file,
)

# 載入定義在 .env 檔案中的環境變數
load_dotenv()
CLIENT_ID = os.getenv("MOTC_TDX_CLIENT_ID")
CLIENT_SECRET = os.getenv("MOTC_TDX_CLIENT_SECRET")

MOTC_TDX_HOST = "https://tdx.transportdata.tw"

DATA_DIR = Path("data/motc-tdx")

# 欲查詢軌道系統
RAIL_SYSTEMS = [
    "TRTC",  # 臺北捷運
    "KRTC",  # 高雄捷運
    "TYMC",  # 桃園捷運
    "TMRT",  # 臺中捷運
    "KLRT",  # 高雄輕軌
    "NTDLRT",  # 淡海輕軌
    "TRTCMG",  # 貓空纜車
    "NTMC",  # 新北捷運
    "NTALRT",  # 安坑輕軌
]


def fetch_motc_tdx_rail_data():
    """Fetch and save Metro data for all TDX rail systems."""
    access_token = get_motc_tdx_access_token()

    # Fetch and save Metro line and station data for each rail system
    for rail_system in RAIL_SYSTEMS:
        fetch_motc_tdx_rail_metro_data(
            access_token=access_token,
            rail_system=rail_system,
        )


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


def fetch_motc_tdx_rail_metro_data(
    access_token: str,
    rail_system: str,
) -> None:
    """Fetch and save Metro station data for one TDX rail system."""
    # fetch rail line data
    response = fetch_motc_tdx_rail_metro_line_data(
        access_token=access_token,
        rail_system=rail_system,
    )
    line_no_list = [line["LineNo"] for line in response]
    print(f"lines: {line_no_list}")


def fetch_motc_tdx_rail_metro_line_data(
    access_token: str,
    rail_system: str,
    top: int = 50,
    skip: int = 0,
    format: str = "JSON",
) -> dict:
    """Fetch and save Metro line data for one TDX rail system."""
    try:
        response = fetch_api(
            f"{MOTC_TDX_HOST}/api/basic/v2/Rail/Metro/Line/{rail_system}",
            method="GET",
            params={
                # "$select": "",
                # "$filter": "",
                # "$orderby": "",
                "$top": top,
                "$skip": skip,
                "$format": format,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        print(
            f"Rail system {rail_system} has {len(response)} lines: {[line['LineNo'] for line in response]}"
        )
        save_json_to_file(response, DATA_DIR / "metro" / rail_system / "line.json")
        time.sleep(1)
        return response
    except Exception as e:
        print(f"Fetching lines for rail system {rail_system} failed: {e}")
        return []
