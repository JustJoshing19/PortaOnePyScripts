import csv
import logging
import os
import sys
import uuid
from getpass import getpass

import requests

from datetime import datetime
from dotenv import load_dotenv
from time import process_time
from tkinter import filedialog

URL = ""

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = "Update_identity_override_" + str(log_time)
logging.basicConfig(filename=logging_name + '.log',
                    filemode='a',
                    format='%(asctime)s, %(msecs)-3d ms || %(name)-22s ' +
                           '%(levelname)-5s ' +
                           '|| %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.NOTSET)
logger = logging.getLogger("Full Import Logger")


# endregion


def get_access_token(usern: str, passw: str) -> str:
    """Get session ID to use for API calls.

    Returns
    -------
        str
            Session ID used for making API calls.
    """
    login_api_url = URL + "Session/login"
    login_body = {
        'params': {
            'login': usern,
            'password': passw
        }}

    t1_start = process_time()
    response = requests.post(login_api_url, json=login_body, verify=False)
    t1_stop = process_time()

    turnaround_time = round((t1_stop - t1_start) * 1000)
    print(turnaround_time)
    print(response.status_code)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        print("An Error Occurred. Check Log")
        sys.exit(1)

    access_token = response.json()['access_token']

    return access_token


def get_sip_accounts(token: str, i_customer: int) -> list[dict]:
    """

    :param token:
    :param i_customer:
    :return:
    """
    ph_list: list[dict] = []
    limit = 100
    offset = 0

    list_accounts_url = "/Account/get_account_list"
    list_accounts_header = {"Authorization": f"Bearer {token}"}
    while True:
        list_accounts_body = {
            "params": {
                "bill_status": "O",
                "billing_model": 1,
                "get_service_features": ["cli"],
                "i_customer": f"{i_customer}",
                "id": "ph%",
                "limit": limit,
                "offset": offset
            }
        }

        response = requests.post(url=list_accounts_url, headers=list_accounts_header,
                                 json=list_accounts_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            print("An Error Occurred")
            sys.exit(1)

        if response.json()["account_list"]:
            ph_list.extend(response.json()["account_list"])
            offset += limit
        else:
            break

    logger.info(f"All SIP accounts retrieved from customer {i_customer}.")
    return ph_list


def update_identity_services(token: str, acc_list: list[dict]) -> bool:
    """

    :param token:
    :param acc_list:
    :return:
    """
    for acc in acc_list:
        acc["service_features"][0]["flag_value"] = "L"
        acc["service_features"][0]["effective_flag_value"] = "L"

    update_list = [[acc["i_account"], acc["service_features"]] for acc in acc_list]

    get_account_info_url = "/Account/update_service_features"
    get_account_info_header = {"Authorization": f"Bearer {token}"}
    for acc in update_list:
        get_account_info_body = {
            "params": {
                "i_account": acc[0],
                "service_features": acc[1]}
        }

        response = requests.post(url=get_account_info_url, headers=get_account_info_header,
                                 json=get_account_info_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            print("An Error Occurred")
            sys.exit(1)

    return True


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")
    token = get_access_token(usern, passw)

    i_customer = int(input("Customer Unique ID: "))
    ph_list = get_sip_accounts(token, i_customer)

    update_identity_services(token, ph_list)
    logger.info(f"All SIP accounts successfully updated for customer {i_customer}")


if __name__ == "__main__":
    main()
