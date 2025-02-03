"""
Script that uses the PortaOne API to move, add, or remove Gijima employee accounts.
"""
import os
from getpass import getpass
from time import process_time

import requests
from dotenv import load_dotenv

EMPLOYEE_PRODUCT_SETS = {"place_holder": [0, None]}


def get_session_id(username: str, password: str) -> str:
    """Get session ID to use for API calls.

    Parameters
    ----------
        username : str
            PortaOne username used to access Porta Billing.
        password : str
            PortaOne user's API token used to request access.

    Returns
    -------
        str
            Session ID used for making API calls.
    """
    login_api_url = "/Session/login"
    login_body = {
        'params': {
            'login': username,
            'password': password
        }}

    t1_start = process_time()
    response = requests.post(login_api_url, json=login_body, verify=False)
    t1_stop = process_time()

    turnaround_time = round((t1_stop - t1_start) * 1000)
    print(turnaround_time)
    print(response.status_code)

    # if response.status_code == 500:
    #     logger.error("An Error Occurred: " + str(response.json()))
    #     input("An Error Occurred. Check Log.")
    #     sys.exit(1)

    session_id = response.json()['access_token']

    return session_id


def get_i_customer() -> int:
    return int(input("What is the i_customer?: "))


def get_ph_account_list(session_id: str, i_customer: int) -> list[dict]:
    phacc_list: list[dict] = []
    offset = 0
    limit = 200
    while True:
        list_accounts_url = "/Account/get_account_list"
        list_accounts_header = {"Authorization": f"Bearer {session_id}"}
        list_accounts_body = {
            "params": {
                "bill_status": "O",
                "billing_model": 1,
                "i_customer": i_customer,
                "id": "ph%",
                "offset": offset,
                "limit": limit
            }
        }
        t1_start = process_time()
        response = requests.post(list_accounts_url, headers=list_accounts_header, json=list_accounts_body, verify=False)
        t1_stop = process_time()
        turnaround_time = round((t1_stop - t1_start) * 1000)

        print(f"Status code: {response.status_code}")
        print(f"Turn around time: {turnaround_time}")

        if not response.json()['account_list']:
            break

        phacc_list.extend(response.json()['account_list'])
        offset += limit

    # logger.info("")
    return phacc_list


def get_ph_account_dids(session_id: str, account_list: list[int]) -> dict[int, str]:
    account_did: dict[int, str] = {}
    for acc in account_list:
        get_alias_list_url = "/Account/get_alias_list"
        get_alias_list_header = {"Authorization": f"Bearer {session_id}"}
        get_alias_list_body = {
            "params": {
                "i_master_account": acc
            }
        }

        t1_start = process_time()
        response = requests.post(get_alias_list_url, headers=get_alias_list_header,
                                 json=get_alias_list_body, verify=False)
        t1_stop = process_time()
        turnaround_time = round((t1_stop - t1_start) * 1000)

        print(response.status_code)
        print(turnaround_time)

        if not response.json()["alias_list"]:
            continue

        account_did[acc] = response.json()["alias_list"][0]["id"]

    return account_did


def update_cli(session_id: str, account_did: list[int]) -> bool:
    for acc in account_did:
        update_account_info_url = "/Account/update_account"
        update_account_info_header = {"Authorization": f"Bearer {session_id}"}
        update_account_info_body = {
            "params": {
                "account_info": {
                    "i_account": acc,
                    "i_product": 18984
                }
            }
        }

        t1_start = process_time()
        response = requests.post(url=update_account_info_url, headers=update_account_info_header,
                                 json=update_account_info_body, verify=False)
        t1_stop = process_time()
        turnaround_time = round((t1_stop - t1_start) * 1000)

        print(response.status_code)
        print(turnaround_time)

    return True


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    session_id = get_session_id(usern, passw)
    i_customer = get_i_customer()
    accounts = get_ph_account_list(session_id, i_customer)
    i_account_list = [x['i_account'] for x in accounts if "#" not in x['id']]
    print(i_account_list)
    # accounts_dids = get_ph_account_dids(session_id, i_account_list)
    # print(accounts_dids)
    print(update_cli(session_id, i_account_list))

    input("Operation complete")
    exit(0)


if __name__ == "__main__":
    main()
