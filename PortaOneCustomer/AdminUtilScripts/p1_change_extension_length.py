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
logging_name = "Change_Extension_Length_" + str(log_time)
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


def get_ext_list(token: str, i_customer: int) -> list[dict]:
    """

    :param token:
    :param i_customer:
    :return:
    """
    limit = 100
    offset = 0
    ext_list: list[dict] = []
    get_extension_list_url = "/Customer/get_extensions_list"
    get_extension_list_header = {"Authorization": f"Bearer {token}"}
    while True:
        get_extension_list_body = {
            "params": {
                "i_customer": i_customer,
                "offset": offset,
                "limit": limit,
                "extension": "05___"
            }
        }

        response = requests.post(url=get_extension_list_url, headers=get_extension_list_header,
                                 json=get_extension_list_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        if not response.json()["extensions_list"]:
            break

        offset += limit
        ext_list.extend(response.json()["extensions_list"])

    return ext_list


def update_ext_length(token: str, ext_list: list[dict]) -> bool:
    """

    :param token:
    :param ext_list:
    :return:
    """
    add_extension_url = "/Customer/update_customer_extension"
    add_extension_header = {"Authorization": f"Bearer {token}"}
    for ext in ext_list:
        add_extension_body = {
            "params": {
                "id": str(ext["id"])[-4:],  # this is the extension number
                "i_customer": ext["i_customer"],
                "i_c_ext": ext["i_c_ext"]
                # //this is Firstname.Lastname from CSV for extension name on cloudpbx
            }
        }

        response = requests.post(url=add_extension_url, headers=add_extension_header, json=add_extension_body,
                                 verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        logger.info(f"Extension {str(ext['id'])[-4:]} updated.")

    logger.info(f"All extensions have been updated.")


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    token = get_access_token(usern, passw)

    try:
        i_customer = int(input("Please provide the customer unique numeral id: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    ext_list = get_ext_list(token, i_customer)
    print(ext_list)

    update_ext_length(token, ext_list)


if __name__ == "__main__":
    main()
