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
logging_name = "Update_Acc_Info_" + str(log_time)
logging.basicConfig(filename=logging_name + '.log',
                    filemode='a',
                    format='%(asctime)s, %(msecs)-3d ms || %(name)-22s ' +
                           '%(levelname)-5s ' +
                           '|| %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.NOTSET)
logger = logging.getLogger("Full Import Logger")


# endregion


def get_ph_accounts(token: str, i_customer: int, sip_prefix="ph") -> list[dict]:
    """

    :param i_customer:
    :param sip_prefix:
    :param token:
    :return:
    """
    i_acc_list: list[dict] = []
    limit = 100
    offset = 0
    get_ph_accounts_url = URL + "Account/get_account_list"
    get_ph_accounts_header = {"Authorization": f"Bearer {token}"}
    while True:
        get_ph_accounts_body = {
            "params": {
                "bill_status": "O",
                "i_customer": i_customer,
                "billing_model": 1,
                "id": (sip_prefix + "%"),
                "limit": limit,
                "offset": offset
            }
        }

        response = requests.post(url=get_ph_accounts_url, headers=get_ph_accounts_header, json=get_ph_accounts_body,
                                 verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        if not response.json()["account_list"]:
            break

        offset += limit
        i_acc_list.extend(response.json()["account_list"])

    logger.info(f"Retrieved Accounts from Customer {i_customer}")
    return i_acc_list


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


def get_acc_email() -> list[dict]:
    """

    :return:
    """
    file_acc_email: list[dict] = []
    with open(filedialog.askopenfilename(), "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for acc in csv_reader:
            acc: dict
            file_acc_email.append(acc)

    return file_acc_email


def update_acc_info(token: str, acc_email_list: list[dict]) -> bool:
    """

    :param token:
    :param acc_email_list:
    :return:
    """
    update_account_services_info_url = "/Account/update_account"
    update_account_services_info_header = {"Authorization": f"Bearer {token}"}
    for acc in acc_email_list:
        update_account_services_info_body = {
            "params": {
                "account_info": {
                    "i_account": acc["i_account"],
                    "email": acc["email"]
                }
            }
        }

        response = requests.post(url=update_account_services_info_url, headers=update_account_services_info_header,
                                 json=update_account_services_info_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            print("An Error Occurred")
            sys.exit(1)

        logger.info(f"Updated Email For Account {acc['i_account']}")

        if acc["costcenter"]:
            update_custom_fields(token, acc['i_account'], acc["costcenter"])

    return True


def update_custom_fields(token: str, i_account: int, costCenter: str) -> bool:
    """

    :param token:
    :param i_account:
    :param costCenter:
    :return:
    """
    update_custom_fields_url = "/Account/update_custom_fields_values"
    update_custom_fields_header = {"Authorization": f"Bearer {token}"}
    update_custom_fields_body = {
        "params": {
            "custom_fields_values": [
                {
                    "db_value": costCenter,
                    "name": "Cost Center"
                }
            ],
            "i_account": i_account
        }
    }

    response = requests.post(url=update_custom_fields_url, headers=update_custom_fields_header,
                             json=update_custom_fields_body, verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    logger.info(f"Custom fields added to Account {i_account}")

    return True


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    token = get_access_token(usern, passw)
    acc_email_list = get_acc_email()
    update_acc_info(token, acc_email_list)

    input("Operation Complete")
    sys.exit(0)


if __name__ == "__main__":
    main()
