from gov_data_fetcher.scrapers.gcis import (
    fetch_gcis_cod_data,
    fetch_gcis_announcement_data,
)
from gov_data_fetcher.scrapers.motc_tdx import fetch_motc_tdx_rail_data


def main() -> None:
    fetch_gcis_announcement_data()
    fetch_gcis_cod_data()
    fetch_motc_tdx_rail_data()


if __name__ == "__main__":
    main()
