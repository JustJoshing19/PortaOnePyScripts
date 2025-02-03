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
URL = ""

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = "Get_account_passwords_" + str(log_time)
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
        print("An Error Occurred")
        sys.exit(1)

    logger.info("Retrieved access token.")
    access_token = response.json()['access_token']

    return access_token


def get_account_info(access_token: str, i_customer: int) -> list[dict]:
    """

    :param access_token:
    :param i_customer:
    :return:
    """
    limit = 300
    offset = 0
    acc_list: list[dict] = []

    list_accounts_url = "/Account/get_account_list"
    list_accounts_header = {"Authorization": f"Bearer {access_token}"}
    while True:
        list_accounts_body = {
            "params": {
                "bill_status": "O",
                "i_customer": f"{i_customer}",
                "id": "ph%",
                "limit": limit,
                "offset": offset
            }
        }

        response = requests.post(url=list_accounts_url, headers=list_accounts_header, json=list_accounts_body,
                                 verify=False)

        if response.status_code != 200:
            logger.error("An Error Occurred: " + str(response.json()))
            print("An Error Occurred.")
            sys.exit(1)

        if not response.json()['account_list']:
            break

        logger.info(f"Next set of accounts retrieved.")
        for acc in response.json()['account_list']:
            department = get_cust_val(access_token, acc["i_account"])
            acc_list.append({
                "h323_password": acc["h323_password"],
                "id": acc["id"],
                "i_account": acc["i_account"],
                "Department": department})

        offset += limit

    logger.info(f"Accounts info for customer {i_customer}")
    return acc_list


def get_cust_val(token: str, i_account: int) -> str:
    get_values_url = "/Account/get_custom_fields_values"
    get_values_header = {"Authorization": f"Bearer {token}"}
    get_values_body = {
        "params": {
            "i_account": i_account  # i_account for PIN_950420_Chris.Terblanche
        }
    }

    response = requests.post(get_values_url, headers=get_values_header, json=get_values_body, verify=False)

    for field in response.json()["custom_fields_values"]:
        if field["name"] == "Department":
            return field["db_value"]

    return ""


def save_acc_info_to_file(acc_list: list[dict], i_customer: int) -> bool:
    keys = list(acc_list[0].keys())

    with open(f"{i_customer}_{datetime.now().date()}.csv", "a", newline="") as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=keys)
        csv_writer.writeheader()
        csv_writer.writerows(acc_list)

    return True


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    token = get_access_token(usern, passw)

    try:
        i_customer = int(input("Provide Customer id: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    acc_list = get_account_info(token, i_customer)

    save_acc_info_to_file(acc_list, i_customer)

    logger.info("Password information retrieved and stored.")
    print("------------------------------------------")
    input("Password information retrieved and stored.")
    sys.exit(0)


if __name__ == "__main__":
    main()
