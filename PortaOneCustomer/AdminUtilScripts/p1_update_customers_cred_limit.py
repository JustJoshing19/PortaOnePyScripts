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
logging_name = "Customer_limits_update_" + str(log_time)
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
    logger.info("Access Token Retrieved")

    return access_token


def get_customer_list(access_token: str, name_filter: str) -> list[dict]:
    """

    :param name_filter:
    :param access_token:
    :return:
    """
    limit = 100
    offset = 0
    cust_list: list[dict] = []
    cust_list_url = URL + "Customer/get_customer_list"
    cust_list_header = {"Authorization": f"Bearer {access_token}"}
    while True:
        cust_list_body = {
            "params": {
                "offset": offset,
                "limit": limit,
                "name": f"{name_filter}%"
            }
        }

        response = requests.post(url=cust_list_url, headers=cust_list_header, json=cust_list_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        offset += limit

        if not response.json()["customer_list"]:
            break

        for cust in response.json()["customer_list"]:
            cust_list.append(cust)

    logger.info(f"All customers retrieved with names starting in {name_filter}...")
    return cust_list


def change_limit(access_token: str, limit: int, cust_list: list[dict]) -> bool:
    """

    :param access_token:
    :param limit:
    :param cust_list:
    :return:
    """
    limit_url = URL + "Customer/update_customer"
    limit_header = {"Authorization": f"Bearer {access_token}"}
    for cust in cust_list:
        limit_body = {
            "params": {
                "customer_info": {
                    "i_customer": cust["i_customer"],
                    "credit_limit": limit
                }
            }
        }

        response = requests.post(url=limit_url, headers=limit_header, json=limit_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        logger.info(f"Customer {cust['i_customer']} credit limit changed to {limit}")

    logger.info("All customers limit changed.")
    return True


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")
    access_token = get_access_token(usern, passw)

    name_filter = input("Please enter the beginning of customers' name: ")

    cust_list = get_customer_list(access_token, name_filter)
    print(cust_list)
    change_limit(access_token, 10000, cust_list)

    logger.info("Operation Complete.")
    input("Operation Complete.")
    sys.exit(0)


if __name__ == "__main__":
    main()
