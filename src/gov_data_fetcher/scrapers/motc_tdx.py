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

# free member: 5 requests per minute
REQUEST_INTERVAL_IN_SECONDS = 15

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
    )  # Print first 10 chars for debugging
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

    # fetch rail station data for each line
    station_list = []
    for line_no in line_no_list:
        response = fetch_motc_tdx_rail_metro_station_data(
            access_token=access_token,
            rail_system=rail_system,
            line=line_no,
        )
        station_list.append(response)
    if len(line_no_list) > 1 and len(station_list) > 1:
        save_json_to_file(
            station_list, DATA_DIR / "metro" / rail_system / "stations.json"
        )

    # fetch rail station data for each line
    station_time_table_list = []
    for line_no in line_no_list:
        response = fetch_motc_tdx_rail_metro_station_time_table(
            access_token=access_token,
            rail_system=rail_system,
            line=line_no,
        )
        station_time_table_list.append(response)
    if len(line_no_list) > 1 and len(station_time_table_list) > 1:
        save_json_to_file(
            station_time_table_list,
            DATA_DIR / "metro" / rail_system / f"station-time-tables.json",
        )


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
        save_json_to_file(response, DATA_DIR / "metro" / rail_system / "lines.json")
        time.sleep(REQUEST_INTERVAL_IN_SECONDS)
        return response
    except Exception as e:
        print(f"Fetching lines for rail system {rail_system} failed: {e}")
        return []


def fetch_motc_tdx_rail_metro_station_data(
    access_token: str,
    rail_system: str,
    line: str,
    top: int = 50,
    skip: int = 0,
    format: str = "JSON",
) -> dict:
    """Fetch and save Metro station data for one TDX rail system."""
    try:
        response = fetch_api(
            f"{MOTC_TDX_HOST}/api/basic/v2/Rail/Metro/Station/{rail_system}",
            method="GET",
            params={
                # "$select": "StationUID,StationID,StationName,SrcUpdateTime",
                "$filter": f"startswith(StationID,'{line}')",
                "$orderby": "StationID",
                "$top": top,
                "$skip": skip,
                "$format": format,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        print(
            f"Fetched {len(response)} stations for rail system {rail_system}, line {line}"
        )
        save_json_to_file(
            response, DATA_DIR / "metro" / rail_system / f"station-{line}.json"
        )
        time.sleep(REQUEST_INTERVAL_IN_SECONDS)
        return response
    except Exception as e:
        print(
            f"Fetching stations for rail system {rail_system}, line {line} failed: {e}"
        )
        return []


def fetch_motc_tdx_rail_metro_station_time_table(
    access_token: str,
    rail_system: str,
    line: str,
    top: int = 60,
    skip: int = 0,
    format: str = "JSON",
) -> dict:
    """Fetch and save Metro station time table for one TDX rail system."""
    try:
        response = fetch_api(
            f"{MOTC_TDX_HOST}/api/basic/v2/Rail/Metro/StationTimeTable/{rail_system}",
            method="GET",
            params={
                # "$select": "StationUID,StationID,StationName,SrcUpdateTime",
                "$filter": f"LineID eq '{line}'",
                "$orderby": "StationID",
                "$top": top,
                "$skip": skip,
                "$format": format,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        print(
            f"Fetched {len(response)} station time table entries for rail system {rail_system}, line {line}"
        )
        response = clean_station_time_table(response)
        if len(response) > 0:
            save_json_to_file(
                response,
                DATA_DIR / "metro" / rail_system / f"station-time-table-{line}.json",
            )
        time.sleep(REQUEST_INTERVAL_IN_SECONDS)
        return response
    except Exception as e:
        print(
            f"Fetching station time table for rail system {rail_system}, line {line} failed: {e}"
        )
        return []


def clean_station_time_table(route_list) -> list:
    """Clean the station time table data by removing unnecessary fields."""
    for route in route_list:
        # replace the Timetables list of dicts with a list of DepartureTime strings
        route["Timetables"] = [item["DepartureTime"] for item in route["Timetables"]]

        # add a new field "ServiceTag" copy from "ServiceDay.ServiceTag"
        if "ServiceDay" in route and "ServiceTag" in route["ServiceDay"]:
            route["ServiceTag"] = route["ServiceDay"]["ServiceTag"]
        else:
            route["ServiceTag"] = None
    return route_list
