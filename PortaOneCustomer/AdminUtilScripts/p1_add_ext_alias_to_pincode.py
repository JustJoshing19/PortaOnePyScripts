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

URL = "/"

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = "" + str(log_time)
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


def get_account_info(token: str, i_account) -> dict:
    """

    :param token:
    :param i_account:
    :return:
    """
    get_account_info_url = "/Account/get_account_info"
    get_account_info_header = {"Authorization": f"Bearer {token}"}
    get_account_info_body = {
        "params": {
            "i_account": i_account  # Account number whose info is going to be requested
        }
    }

    t1_start = process_time()
    response = requests.post(get_account_info_url, headers=get_account_info_header,
                             json=get_account_info_body, verify=False)
    t1_stop = process_time()
    turnaround_time = round((t1_stop - t1_start) * 1000)
    print(f"turn around time: {turnaround_time}")

    acc_details = {"id": response.json()["account_info"]["id"],
                   "i_account": response.json()["account_info"]["i_account"],
                   "i_customer": response.json()["account_info"]["i_customer"]}
    return acc_details


def get_pincode_accounts(token: str, i_customer: int) -> list[dict]:
    """

    :param token:
    :param i_customer:
    :return:
    """
    limit = 100
    offset = 0
    pincode_alias_list: list[dict] = []
    list_accounts_url = "/Account/get_account_list"
    list_accounts_header = {"Authorization": f"Bearer {token}"}
    while True:
        list_accounts_body = {
            "params": {
                "bill_status": "O",
                "i_customer": f"{i_customer}",
                "id": "pin%",
                "limit": limit,
                "offset": offset,
                "billing_model": 1,
                "with_aliases": 1
            }
        }

        response = requests.post(list_accounts_url,
                                 headers=list_accounts_header,
                                 json=list_accounts_body,
                                 verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        if not response.json()["account_list"]:
            break

        for pin_acc in response.json()["account_list"]:
            pincode_alias_list.append({
                "pin_i_acc": pin_acc["i_account"],
                "id": pin_acc["id"],
                "alias_list": pin_acc["alias_list"]
            })
        offset += limit

    return pincode_alias_list


def get_alias_updates(pin_list: list[dict], acc_details: dict) -> list[dict]:
    """

    :param pin_list:
    :param acc_details:
    :return:
    """
    update_list: list[dict] = []
    for pin in pin_list:
        alias_list: list[str] = []

        for alias in pin["alias_list"]:
            alias_list.append(alias["id"][8:12])
        if acc_details["id"][8:] in alias_list:
            break
        else:
            update_list.append({
                "pin": pin["id"].split("_")[1],
                "i_master_account": pin["pin_i_acc"]
            })

    return update_list


def add_alias(token: str, update_list: list[dict], acc_details: dict) -> bool:
    """

    :param token:
    :param update_list:
    :param acc_details:
    :return:
    """
    add_alias_url = URL + "Account/add_alias"
    add_alias_header = {"Authorization": f"Bearer {token}"}
    for pincode in update_list:
        add_alias_body = {
            "params": {
                "alias_info": {
                    "i_master_account": pincode["i_master_account"],
                    "i_account": acc_details["i_account"],
                    "id": f"{acc_details['id']}#{pincode['pin']}"
                }
            }
        }

        t1_start = process_time()
        response = requests.post(add_alias_url, headers=add_alias_header,
                                 json=add_alias_body, verify=False)
        t1_stop = process_time()
        turnaround_time = round((t1_stop - t1_start) * 1000)

        print(turnaround_time)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            print("An Error Occurred")
            sys.exit(1)

    return True


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    try:
        i_account = int(input("Account unique ID: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    token = get_access_token(usern, passw)
    acc_details = get_account_info(token, i_account)
    if acc_details:
        i_customer = acc_details["i_customer"]
        pin_list = get_pincode_accounts(token, i_customer)
        update_list = get_alias_updates(pin_list, acc_details)
        add_alias(token, update_list, acc_details)

    input("Aliases added to pincodes.")
    exit(0)


if __name__ == "__main__":
    main()
