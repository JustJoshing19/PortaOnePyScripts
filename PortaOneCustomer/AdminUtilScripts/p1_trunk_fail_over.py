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
logging_name = "DID_Mover_" + str(log_time)
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

    logger.info("Access Token Retrieved.")
    access_token = response.json()['access_token']

    return access_token


def get_account_i_dids(access_token: str, i_account: int) -> list[int]:
    """

    :param access_token:
    :param i_account:
    :return:
    """
    i_did_list: list[int] = []
    offset = 0
    limit = 200

    i_did_url = URL + "Account/get_alias_list"
    i_did_header = {"Authorization": f"Bearer {access_token}"}
    while True:
        i_did_body = {
            "params": {
                "i_master_account": i_account,
                "offset": offset,
                "limit": limit
            }
        }

        response = requests.post(url=i_did_url, headers=i_did_header, json=i_did_body, verify=False)

        if response.status_code == 500:
            logger.error("An error Occurred: " + str(response.json()))
            sys.exit(1)

        if not response.json()["alias_list"]:
            break

        for i_did in response.json()["alias_list"]:
            i_did_list.append(i_did)

        offset += limit

    logger.info("All alias retrieved.")
    return i_did_list


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    token = get_access_token(usern=usern, passw=passw)

    try:
        i_account = int(input("Please provide trunk account id: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    did_list = get_account_i_dids(token, i_account)

    logger.info("Operation complete.")
    input("Operation complete.")
    sys.exit(0)


if __name__ == "__main__":
    main()
