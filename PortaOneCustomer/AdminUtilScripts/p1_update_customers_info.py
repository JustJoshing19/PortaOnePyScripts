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
logging_name = "Update_Customers_Info_" + str(log_time)
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

    access_token = response.json()['access_token']

    return access_token


def get_customer_list(token: str, name: str) -> list[dict]:
    """

    :param token:
    :param name:
    :return:
    """
    limit = 100
    offset = 0
    customer_list: list[dict] = []
    get_account_info_url = "/Customer/get_customer_list"
    get_account_info_header = {"Authorization": f"Bearer {token}"}
    while True:
        get_account_info_body = {
            "params": {
                "bill_status": "O",
                "name": f"{name}%",
                "limit": limit,
                "offset": offset
            }
        }

        response = requests.post(url=get_account_info_url, headers=get_account_info_header,
                                 json=get_account_info_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        if not response.json()["customer_list"]:
            break

        offset += limit

        logger.info(f"List Retrieved")
        customer_list.extend(response.json()["customer_list"])

    return customer_list


def update_cust_info(token: str, i_customer: int) -> bool:
    """

    :param token:
    :param i_customer:
    :return:
    """
    update_customer_info_url = "/Customer/update_customer"
    update_customer_info_header = {"Authorization": f"Bearer {token}"}
    update_customer_info_body = {
        "params": {
            "customer_info": {
                "i_customer": i_customer,
                "bcc": "d1aeffad.gijima.com@emea.teams.ms,chris.terblanche@gijima.com",
                "credit_limit_warning": [
                    {
                        "type": "P",
                        "warning_threshold": 80
                    },
                    {
                        "type": "P",
                        "warning_threshold": 85
                    },
                    {
                        "type": "P",
                        "warning_threshold": 90
                    },
                    {
                        "type": "P",
                        "warning_threshold": 93
                    },
                    {
                        "type": "P",
                        "warning_threshold": 95
                    },
                    {
                        "type": "P",
                        "warning_threshold": 97
                    },
                    {
                        "type": "P",
                        "warning_threshold": 98
                    },
                    {
                        "type": "P",
                        "warning_threshold": 99
                    }
                ]
            }
        }}

    response = requests.post(url=update_customer_info_url, headers=update_customer_info_header,
                             json=update_customer_info_body, verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    logger.info(f"Updated customer {i_customer} bcc and credit_limit_warning")

    return True


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    token = get_access_token(usern, passw)

    customer_name = input("Please provide the prefix of the customers (Leave empty to update all customers): ")
    customer_list = get_customer_list(token, customer_name)

    for i_customer in customer_list:
        update_cust_info(token, i_customer["i_customer"])

    logger.info(f"Operation Complete")
    input("Operation Complete")
    sys.exit(0)


if __name__ == "__main__":
    main()
