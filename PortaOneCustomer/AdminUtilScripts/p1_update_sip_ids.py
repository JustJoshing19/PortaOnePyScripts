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
logging_name = "p1_Update_SIP_IDs_" + str(log_time)
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


def get_file_sip_accounts() -> list[dict]:
    """

    :return:
    """
    file_accs: list[dict] = []
    with open(filedialog.askopenfilename(), "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for acc in csv_reader:
            acc: dict
            file_accs.append(acc)

    return file_accs


def get_site_accs(token: str, i_customer: int) -> list[dict]:
    """

    :param token:
    :param i_customer:
    :return:
    """
    site_accs: list[dict] = []
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
                "id": "ph%",
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
        site_accs.extend(response.json()["account_list"])

    logger.info(f"Retrieved Accounts from Customer {i_customer}")
    return site_accs


def compare_accs(file_accs: list[dict], site_accs: list[dict]) -> list[dict]:
    """

    :param file_accs:
    :param site_accs:
    :return:
    """
    matched_accs: list[dict] = []

    for f_acc in file_accs:
        found: bool = False
        for s_acc in site_accs:
            s_acc_ext = str(s_acc["id"]).split("x")[-1]
            if f_acc["ext"] == s_acc_ext:
                matched_accs.append({
                    "i_account": s_acc["i_account"],
                    "number": f_acc["number"]
                })
                found = True
                break

        if not found:
            logger.info(f"Extension {f_acc['ext']} was not found.")

    return matched_accs


def update_acc_id(token: str, matched_list: list[dict]) -> bool:
    """

    :param token:
    :param matched_list:
    :return:
    """
    update_account_info_url = "/Account/update_account"
    update_account_info_header = {"Authorization": f"Bearer {token}"}
    for acc in matched_list:
        update_account_info_body = {
            "params": {
                "account_info": {
                    "i_account": acc["i_account"],
                    "id": acc["number"]
                }
            }
        }

        response = requests.post(url=update_account_info_url, headers=update_account_info_header,
                                 json=update_account_info_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        logger.info(f"Account {acc['i_account']} has been updated.")

    return True


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    try:
        i_customer = int(input("Please provide the customer sites unique numeral id: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    token = get_access_token(usern, passw)

    file_accs = get_file_sip_accounts()
    site_accs = get_site_accs(token, i_customer)
    matched_list = compare_accs(file_accs, site_accs)
    update_acc_id(token, matched_list)

    input("Operation Complete")
    sys.exit(0)


if __name__ == "__main__":
    main()
