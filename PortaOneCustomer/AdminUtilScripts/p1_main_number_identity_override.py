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
logging_name = "Main_number_identity_override_" + str(log_time)
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
    logger.info("Access Token Retrieved")

    return access_token


def get_no_alias_accounts(token: str, i_customer: int) -> list[dict]:
    """

    :param token:
    :param i_customer:
    :return:
    """
    acc_list: list[dict] = []
    limit = 200
    offset = 0

    acc_url = URL + "Account/get_account_list"
    acc_header = {"Authorization": f"Bearer {token}"}
    while True:
        acc_body = {
            "params": {
                "bill_status": "O",
                "i_customer": i_customer,
                "id": "ph%",
                "limit": limit,
                "offset": offset,
                "billing_model": 1,
                "with_aliases": 1
            }
        }

        response = requests.post(url=acc_url, headers=acc_header, json=acc_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        if not response.json()["account_list"]:
            break

        offset += limit
        acc_list.extend([acc for acc in response.json()["account_list"] if not acc["alias_list"]])

    logger.info("All accounts without aliases")
    return acc_list


def update_identity_override(token: str, acc_list: list[dict], main_num: str) -> bool:
    """

    :param acc_list:
    :param main_num:
    :param token:
    :return:
    """
    update_account_identity_override_url = "/Account/update_service_features"
    update_account_identity_override_header = {"Authorization": f"Bearer {token}"}
    for acc in acc_list:
        update_account_identity_override_body = {
            "params": {
                "i_account": acc["i_account"],
                "service_features": [{
                    "attributes": [
                        {
                            "effective_values": [
                                main_num
                            ],
                            "name": "centrex",
                            "values": [
                                main_num
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

        response = requests.post(url=update_account_identity_override_url,
                                 headers=update_account_identity_override_header,
                                 json=update_account_identity_override_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        logger.info(f"Account identity override of account {acc['i_account']} changed to {main_num}.")

    return True


def main():
    print("---------------")
    print("Changes the identity override of a account to the main number if they don't have their own alias.")
    print("---------------")

    usern = input("Username: ")
    passw = getpass("Password: ")

    try:
        i_customer = int(input("Customer id: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    main_num = input("Main number: ")
    if len(main_num) != 11:
        logger.error("Number is not 11 numbers long ('27' prefix included).")
        input("An Error Occurred. Number is not 11 numbers long ('27' prefix included).")
        sys.exit(1)

    token = get_access_token(usern, passw)
    acc_list = get_no_alias_accounts(token, i_customer)
    update_identity_override(token, acc_list, main_num)

    logger.info("Operation Complete.")
    input("Operation Complete.")
    sys.exit(0)


if __name__ == "__main__":
    main()
