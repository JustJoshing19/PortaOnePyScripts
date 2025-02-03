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
logging_name = "Remove_Accounts_Subscriptions_" + str(log_time)
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


def get_subscriptions(token: str, i_customer: int) -> list[dict]:
    """

    :param i_customer:
    :param token:
    :return:
    """
    limit = 200
    offset = 0
    acc_sub_list: list[dict] = []
    url_get_sub = URL + "Customer/get_accounts_subscriptions"
    header_get_sub = {"Authorization": f"Bearer {token}"}
    while True:
        body_get_sub = {
            "params": {
                "i_customer": i_customer,
                "limit": limit,
                "offset": offset
            }
        }

        response = requests.post(url=url_get_sub, headers=header_get_sub, json=body_get_sub, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        if not response.json()["subscriptions"]:
            break

        offset += limit
        acc_sub_list.extend(response.json()["subscriptions"])

    logger.info(f"All subscriptions retrieved from customer {i_customer}")
    return acc_sub_list


def filter_subscriptions(acc_sub_list: list[dict], i_subscription: int) -> list[dict]:
    """

    :param acc_sub_list:
    :param i_subscription:
    :return:
    """
    filtered_acc_sub_list: list[dict] = []
    for acc_sub in acc_sub_list:
        if acc_sub["i_subscription"] == i_subscription:
            filtered_acc_sub_list.append(acc_sub)

    logger.info(f"Subscriptions filtered to Subscription {i_subscription}")
    return filtered_acc_sub_list


def remove_subscription(token: str, acc_sub_list: list[dict]) -> bool:
    """

    :param token:
    :param acc_sub_list:
    :return:
    """
    close_sub_url = URL + "Account/close_subscription"
    delete_sub_header = {"Authorization": f"Bearer {token}"}
    for sub in acc_sub_list:
        close_sub_body = {
            "params": {
                "i_account_subscription": sub["i_account_subscription"]
            }
        }

        response = requests.post(url=close_sub_url, headers=delete_sub_header, json=close_sub_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        logger.info(f"Subscription {sub['i_subscription']} closed on account {sub['i_account']}.")

    logger.info(f"All Subscriptions removed from customer.")
    return True


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    token = get_access_token(usern, passw)

    try:
        i_customer = int(input("Please provide customer unique numeral id: "))
        i_subscription = int(input("Please provide the subscription unique numeral id that you want removed: "))
        logger.info(f"Customer = {i_customer}, Subscription = {i_subscription}")
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    acc_sub_list = get_subscriptions(token, i_customer)
    acc_sub_list = filter_subscriptions(acc_sub_list, i_subscription)
    print(acc_sub_list)
    remove_subscription(token, acc_sub_list)

    input("Operation Complete.")
    exit(0)


if __name__ == "__main__":
    main()
