import os
from dotenv import load_dotenv

# 載入定義在 .env 檔案中的環境變數
load_dotenv()
CLIENT_ID = os.getenv("MOTC_TDX_CLIENT_ID")
CLIENT_SECRET = os.getenv("MOTC_TDX_CLIENT_SECRET")


def fetch_motc_tdx_rail_data():
    """Fetch and save rail data for all TDX rail systems."""
    print(f"CLIENT_ID: {CLIENT_ID}")
    print(f"CLIENT_SECRET: {CLIENT_SECRET}")
