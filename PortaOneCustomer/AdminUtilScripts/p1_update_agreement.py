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

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = "Update_Agreement_" + str(log_time)
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
    """Create a login session to make API calls.

    :return: The access token used to make API calls.
    """
    login_api_url = "/Session/login"
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


def get_account_list(access_token: str, i_customer: int) -> list:
    # Make call to API to retrieve a list of accounts that belong to the given customer ID (i_customer)

    limit = 200
    offset = 0
    acc_list: list[dict] = []
    list_accounts_url = "/Account/get_account_list"
    list_accounts_header = {"Authorization": f"Bearer {access_token}"}
    while True:
        list_accounts_body = {
            "params": {
                "bill_status": "O",
                "i_customer": f"{i_customer}",
                "billing_model": 1,
                "id": "ph%",
                "limit": limit,
                "offset": offset
            }
        }
        t1_start = process_time()
        response = requests.post(list_accounts_url, headers=list_accounts_header, json=list_accounts_body, verify=False)
        t1_stop = process_time()
        turnaround_time = round((t1_stop - t1_start) * 1000)

        print(f"Status code: {response.status_code}")
        print(f"Turn around time: {turnaround_time}")

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        if not response.json()["account_list"]:
            break

        offset += limit
        acc_list.extend(response.json()["account_list"])

    print(f"Full List: {response.json()}")

    logger.info(f"All accounts retrieved from customer {i_customer}")
    return acc_list


def get_product_list(acc_list: list[dict]) -> dict[int:int]:
    """

    :param acc_list:
    :return:
    """
    prod_list: dict[int, int] = {}
    for data in acc_list:
        i_prod = data["i_product"]
        if i_prod in list(prod_list.keys()):
            prod_list[i_prod] += 1
        else:
            prod_list[i_prod] = 1

    return prod_list


def update_agreement(token: str, i_customer: int, prod_list: dict) -> bool:
    """

    :param token:
    :param i_customer:
    :param prod_list:
    :return:
    """
    agreement_list: list[dict] = []
    for key in list(prod_list.keys()):
        agreement_list.append({"i_product": key,
                               "max_offered_quantity": prod_list[key]})

    update_agreement_url = "/Customer/update_agreement_conditions"
    update_agreement_header = {"Authorization": f"Bearer {token}"}
    update_agreement_body = {
        "params": {
            "agreement_condition_list": agreement_list,
            "i_customer": i_customer
        }
    }

    response = requests.post(url=update_agreement_url, headers=update_agreement_header,
                             json=update_agreement_body, verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    logger.info(f"Agreements for customer {i_customer} updated.")
    return True


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    access_token = get_access_token(usern, passw)
    try:
        i_customer = int(
            input("Please provide the unique identifier of the customer whose account list should be retrieved:\n"))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    acc_list = get_account_list(access_token, i_customer)
    prod_list = get_product_list(acc_list)

    print(prod_list)

    update_agreement(access_token, i_customer, prod_list)

    logger.info("Operation Complete.")
    input("Operation Complete")
    sys.exit(0)


if __name__ == "__main__":
    main()
