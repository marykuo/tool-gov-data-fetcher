GCIS_HOST = "https://gcis.nat.gov.tw"


def fetch_cod_data(gcis_host: str = GCIS_HOST):
    """
    大類 Section
    中類 Division
    小類 Group
    細類 Class
    """
    print("Fetching COD data from GCIS...")
