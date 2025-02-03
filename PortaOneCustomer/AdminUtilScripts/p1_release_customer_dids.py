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
logging_name = "Release_Customer_DIDs_" + str(log_time)
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

    return access_token


def release_account_alias(token: str, i_customer: int) -> bool:
    """

    :param token:
    :param i_customer:
    :return:
    """
    alias_i_acc_list: list[int] = []
    alias_acc_list_url = URL + "Account/get_account_list"
    alias_acc_list_header = {"Authorization": f"Bearer {token}"}
    limit = 200
    offset = 0
    while True:
        alias_acc_list_body = {
            "params": {
                "billing_model": 2,
                "bill_status": "O",
                "i_customer": i_customer,
                "id": "27%",
                "limit": limit,
                "offset": offset
            }
        }

        response = requests.post(url=alias_acc_list_url, headers=alias_acc_list_header, json=alias_acc_list_body,
                                 verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        if not response.json()["account_list"]:
            break

        for acc in response.json()["account_list"]:
            alias_i_acc_list.append(acc["i_account"])

        offset += limit

    remove_alias_url = URL + "Account/delete_alias"
    remove_alias_header = {"Authorization": f"Bearer {token}"}
    for alias in alias_i_acc_list:
        remove_alias_body = {
            "params": {
                "alias_info": {
                    "i_account": alias
                },
                "release_assigned_did": 1
            }
        }

        response = requests.post(url=remove_alias_url, headers=remove_alias_header, json=remove_alias_body,
                                 verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

    return True


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    token = get_access_token(usern, passw)

    try:
        i_customer = int(input("Unique customer id: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    release_account_alias(token, i_customer)

    input("Operation Complete")


if __name__ == "__main__":
    main()
