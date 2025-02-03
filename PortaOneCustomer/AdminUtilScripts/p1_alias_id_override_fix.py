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

load_dotenv("env/.env")

TOKEN = os.getenv("API_TOKEN")
USERNAME = os.getenv("USER")
URL = os.getenv("URL")

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = "Alias_Identity_Override_" + str(log_time)
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
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    access_token = response.json()['access_token']

    logger.info("Retrieved access token.")
    return access_token


def get_accounts(token: str, i_customer: int) -> list[dict]:
    """

    :param token:
    :param i_customer:
    :return:
    """
    limit = 100
    offset = 0

    ph_url = URL + "Account/get_account_list"
    ph_header = {"Authorization": f"Bearer {token}"}
    acc_list: list[dict] = []

    while True:
        ph_body = {
            "params": {
                "bill_status": "O",
                "billing_model": 2,
                "i_customer": i_customer,
                "id": "27%",
                "offset": offset,
                "limit": limit
            }
        }

        response = requests.post(url=ph_url, headers=ph_header, json=ph_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))

        for data in response.json()["account_list"]:
            if data["i_product"] == 14409:
                continue
            acc_list.append(data)

        if not response.json()["account_list"]:
            break

        offset += limit

    logger.info(f"All accounts retrieved from customer {i_customer}")
    return acc_list


def update_identity_override(token: str, acc_list: list[dict]) -> bool:
    """

    :param token:
    :param acc_list:
    :return:
    """
    update_account_services_info_url = "/Account/update_service_features"
    update_account_services_info_header = {"Authorization": f"Bearer {token}"}
    for acc in acc_list:
        update_account_services_info_body = {
            "params": {
                "i_account": acc["i_master_account"],
                "service_features": [{
                    "attributes": [
                        {
                            "effective_values": [
                                acc["id"]
                            ],
                            "name": "centrex",
                            "values": [
                                acc["id"]
                            ]
                        },
                        {
                            "effective_values": [
                                ""
                            ],
                            "name": "display_number",
                            "values": [
                                ""
                            ]
                        }
                    ],
                    "effective_flag_value": "Y",
                    "flag_value": "Y",
                    "locked": 0,
                    "locks": [],
                    "name": "cli"
                }]
            }
        }

        response = requests.post(url=update_account_services_info_url, headers=update_account_services_info_header,
                                 json=update_account_services_info_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            print("An Error Occurred")
            sys.exit(1)

        logger.info(f"Update identity override for account {acc['i_master_account']}")

    logger.info("All accounts identity override updated.")
    return True


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    token = get_access_token(usern, passw)

    try:
        i_customer = int(input("Customer id: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    acc_list = get_accounts(token, i_customer)
    update_identity_override(token, acc_list)

    logger.info("Operation complete.")
    input("Operation complete.")
    sys.exit(0)


if __name__ == "__main__":
    main()
