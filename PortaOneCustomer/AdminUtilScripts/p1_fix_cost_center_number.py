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
logging_name = "Fix_Cost_Center_Number_" + str(log_time)
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
    logger.info("Access Token Retrieved.")

    return access_token


def get_acc_list(access_token: str, i_customer: int) -> list[int]:
    """

    :param access_token:
    :param i_customer:
    :return:
    """
    limit = 100
    offset = 0

    ph_url = URL + "Account/get_account_list"
    ph_header = {"Authorization": f"Bearer {access_token}"}
    i_account_list: list[int] = []

    while True:
        ph_body = {
            "params": {
                "bill_status": "O",
                "billing_model": 1,
                "i_customer": i_customer,
                "id": "ph%",
                "offset": offset,
                "limit": limit
            }
        }

        response = requests.post(url=ph_url, headers=ph_header, json=ph_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))

        for data in response.json()["account_list"]:
            i_account_list.append(data["i_account"])

        if not response.json()["account_list"]:
            break

        offset += limit

    logger.info(f"Accounts retrieved from customer {i_customer}.")
    return i_account_list


def get_custom_values(token: str, i_acc_list: list[int]) -> list[dict]:
    """

    :param token:
    :param i_acc_list:
    :return:
    """
    custom_values: list[dict] = []
    custom_values_url = URL + "Account/get_custom_fields_values"
    custom_values_header = {"Authorization": f"Bearer {token}"}
    for acc in i_acc_list:
        custom_values_body = {
            "params": {
                "i_account": acc
            }
        }

        response = requests.post(url=custom_values_url, headers=custom_values_header,
                                 json=custom_values_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        for val in response.json()["custom_fields_values"]:
            if val["name"] == "Cost Center":
                custom_values.append({
                    "acc": acc,
                    "db_value": val["db_value"],
                    "name": val["name"]
                })

        logger.info(f"Retrieved custom values for account {acc}.")

    return custom_values


def fix_value(custom_values: list[dict]) -> list[dict]:
    """

    :param custom_values:
    :return:
    """

    for val in custom_values:

        num = val["db_value"]
        old = val["db_value"]
        if not num:
            num = "9999"
        else:
            num = num.zfill(4)
        val["db_value"] = num
        logger.info(f"Cost center value changed from {old} to {num}")

    logger.info(f"All cost center values fixed.")
    return custom_values


def update_custom_values(token: str, custom_values: list[dict]) -> bool:
    """

    :param token:
    :param custom_values:
    :return:
    """
    custom_values_url = URL + "Account/update_custom_fields_values"
    custom_values_header = {"Authorization": f"Bearer {token}"}
    for val in custom_values:
        custom_values_body = {
            "params": {
                "custom_fields_values": [
                    {
                        "db_value": val["db_value"],
                        "name": val["name"]
                    }
                ],
                "i_account": val["acc"]
            }
        }

        response = requests.post(url=custom_values_url, headers=custom_values_header,
                                 json=custom_values_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        logger.info(f"Cost Center value updated for account {val['acc']}")

    return True


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    token = get_access_token(usern, passw)

    try:
        i_customer = int(input("Please provide customer id: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    logger.info(f"Customer id retrieved: {i_customer}")

    acc_list = get_acc_list(token, i_customer)

    custom_values = get_custom_values(token, acc_list)
    logger.info(f"All account custom values retrieved from customer {i_customer}")

    custom_values = fix_value(custom_values)

    update_custom_values(token, custom_values)
    logger.info(f"All custom values for customer {i_customer} have been updated.")

    logger.info("Operation Complete.")
    input("Operation Complete")
    sys.exit(0)


if __name__ == "__main__":
    main()
