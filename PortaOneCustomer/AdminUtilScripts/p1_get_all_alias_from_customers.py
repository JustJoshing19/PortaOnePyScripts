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
logging_name = "Get_Alias_From_Customers_" + str(log_time)
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


def get_customers(token: str, name: str) -> list[int]:
    """

    :param token:
    :param name:
    :return:
    """

    get_customer_url = URL + "Customer/get_customer_list"
    get_customer_header = {"Authorization": f"Bearer {token}"}
    get_customer_body = {
        "params": {
            "name": f"{name}%"
        }
    }

    response = requests.post(url=get_customer_url, headers=get_customer_header, json=get_customer_body,
                             verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    i_customer_list: list[int] = [customer["i_customer"] for customer in response.json()["customer_list"]]

    return i_customer_list


def get_aliases(token: str, i_customer_list: list[int]) -> dict[int, list[str]]:
    """

    :param token:
    :param i_customer_list:
    :return:
    """
    account_alias_dict: dict[int, list[str]] = {}
    alias_acc_list_url = URL + "Account/get_account_list"
    alias_acc_list_header = {"Authorization": f"Bearer {token}"}

    for i_customer in i_customer_list:
        limit = 200
        offset = 0
        while True:
            alias_acc_list_body = {
                "params": {
                    "billing_model": 1,
                    "bill_status": "O",
                    "i_customer": i_customer,
                    "limit": limit,
                    "offset": offset,
                    "with_aliases": 1
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
                account_alias_dict[acc["id"]] = [alias["id"] for alias in acc["alias_list"]]

            offset += limit

    return account_alias_dict


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    token = get_access_token(usern, passw)

    customer_name = input("Customer name prefix: ")
    i_cust_list = get_customers(token, customer_name)

    print(i_cust_list)

    acc_alias_dict = get_aliases(token, i_cust_list)

    print(acc_alias_dict)


if __name__ == "__main__":
    main()
