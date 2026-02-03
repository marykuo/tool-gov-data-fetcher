from gov_data_fetcher.core.utility import fetch_api, save_json_to_file


GCIS_HOST = "https://gcis.nat.gov.tw"


def fetch_cod_data(gcis_host: str = GCIS_HOST):
    """
    大類 Section
    中類 Division
    小類 Group
    細類 Class
    """
    print("\n=== Fetching COD Data ===")

    # fetch section codes
    section_code_list = fetch_section_codes(gcis_host)

    # fetch division, group
    child_list_by_section = fetch_child_codes(gcis_host, section_code_list)
    fetch_division_codes(section_code_list, child_list_by_section)
    group_list_by_section = fetch_group_codes(child_list_by_section, section_code_list)

    # fetch full codes
    fetch_full_codes(gcis_host, section_code_list, group_list_by_section)


def fetch_section_codes(gcis_host):
    print("\n=== Fetching Section Codes ===")
    response = fetch_api(f"{gcis_host}/elawCodAp/api/codeSearch/getAllMainCode")

    # save raw response
    save_json_to_file(response, "data/gcis/main_code/raw_main_code.json")

    # save processed section list
    section_full_list = response
    save_json_to_file(section_full_list, "data/gcis/1_section_code.json")

    # extract section code list
    section_code_list = [item["code"] for item in section_full_list]
    print(section_code_list)
    return section_code_list


def fetch_child_codes(gcis_host, section_code_list):
    print("\n=== Fetching Child Codes ===")
    full_child_list = []
    child_list_by_section = {code: None for code in section_code_list}
    for section_code in section_code_list:
        response = fetch_api(
            f"{gcis_host}/elawCodAp/api/codeSearch/getAllChildCode?mainCode={section_code}"
        )
        # save raw response
        save_json_to_file(
            response, f"data/gcis/child_code/raw_child_code_{section_code}.json"
        )
        # append to full list
        full_child_list.append(response)
        # store by section
        child_list_by_section[section_code] = response
        print(
            f"Section {section_code} has {len(response['codeSearchDto'])} division codes"
        )

    # save full raw child list
    save_json_to_file(full_child_list, "data/gcis/child_code/all_child_code.json")
    return child_list_by_section


def fetch_division_codes(section_code_list, child_list_by_section):
    print("\n=== Fetching Division Codes ===")
    division_full_list = []
    for section_code in section_code_list:
        # extract division list
        division_list = child_list_by_section[section_code]["codeSearchDto"]

        # clean up division items
        for division_item in division_list:
            # create new item without empty sub-codes
            new_item = {k: v for k, v in division_item.items() if k != "codeSearchDto"}
            division_full_list.append(new_item)

        # print division codes
        print([item["code"] for item in division_list])

    # save full processed division list
    save_json_to_file(division_full_list, "data/gcis/2_division_code.json")


def fetch_group_codes(child_list_by_section, section_code_list):
    print("\n=== Fetching Group Codes ===")
    group_full_list = []
    group_list_by_section = {code: [] for code in section_code_list}
    for section_code in section_code_list:
        # extract division list
        division_list = child_list_by_section[section_code]["codeSearchDto"]

        # extract group codes from each division
        for division_item in division_list:
            group_list = division_item["codeSearchDto"]
            for group_item in group_list:
                # create new item without empty sub-codes
                new_item = {k: v for k, v in group_item.items() if k != "codeSearchDto"}
                group_full_list.append(new_item)
                group_list_by_section[section_code].append(new_item["code"])

        # print group codes of each section
        print(group_list_by_section[section_code])

    # save full processed group list
    save_json_to_file(group_full_list, "data/gcis/3_group_code.json")
    return group_list_by_section


def fetch_full_codes(gcis_host, section_code_list, group_list_by_section):
    print("\n=== Fetching Full Codes ===")
    full_code_list = []
    full_codes_by_section = {code: [] for code in section_code_list}
    # iterate over group codes to fetch full codes
    for section_code in section_code_list:
        for group_code in group_list_by_section[section_code]:
            response = fetch_api(
                f"{gcis_host}/elawCodAp/api/codeSearch/getAllFullCode?thiCode={group_code}"
            )
            for full_code in response:
                full_codes_by_section[section_code].append(full_code)
                full_code_list.append(full_code)

        # save full codes of each section
        save_json_to_file(
            full_codes_by_section[section_code],
            f"data/gcis/full_code/full_code_{section_code}.json",
        )
        print(
            f"Section {section_code} has {len(full_codes_by_section[section_code])} full codes"
        )

    # save full processed full code list
    save_json_to_file(full_code_list, "data/gcis/4_full_code.json")
