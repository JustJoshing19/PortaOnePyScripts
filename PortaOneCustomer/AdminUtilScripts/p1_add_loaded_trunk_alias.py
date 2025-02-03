import csv
import logging
import os
import sys

from datetime import datetime
from time import process_time
from tkinter import filedialog

import requests
from dotenv import load_dotenv

load_dotenv("env/.env")

TOKEN = os.getenv("API_TOKEN")
USERNAME = "joshuar"
DID_GROUPS = {"ICASA": 24, "PORTEDNUMBERS": 35}
NUMBER_RANGES = ["2710133", "2712133", "2713133", "2714133", "2721133",
                 "2731393", "2741133", "2751133", "2787463", "2786"]

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = "Add_trunk_aliases_" + str(log_time)
logging.basicConfig(filename=logging_name + '.log',
                    filemode='a',
                    format='%(asctime)s, %(msecs)-3d ms || %(name)-22s ' +
                           '%(levelname)-5s ' +
                           '|| %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.NOTSET)
logger = logging.getLogger("Full Import Logger")


# endregion


def get_access_token(username: str, api_token: str) -> str:
    """Get session ID to use for API calls.

    Parameters
    ----------
        username : str
            PortaOne username used to access Porta Billing.
        api_token : str
            PortaOne user's API token used to request access.

    Returns
    -------
        str
            Session ID used for making API calls.
    """
    login_api_url = "/Session/login"
    login_body = {
        'params': {
            'login': username,
            'token': api_token
        }}

    t1_start = process_time()
    response = requests.post(login_api_url, json=login_body, verify=False)
    t1_stop = process_time()

    turnaround_time = round((t1_stop - t1_start) * 1000)
    print(turnaround_time)
    print(response.status_code)

    access_token = response.json()['access_token']

    return access_token


def get_alias_numbers() -> list[str]:
    """Get a list of alias number sto be added to a gateway pilot account.

    :return: A list of alias numbers.
    """
    alias_numbers: list[str] = []

    try:
        file_path = filedialog.askopenfilename()
        if file_path.find(".csv") == -1:
            logger.error("File is not a CSV file.")
            input("An error occurred. Check log.")
            sys.exit(1)

        with open(file_path, "r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                row: dict
                alias_numbers.append(row["Number"])
    except IndexError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An error occurred. Check log.")
        sys.exit(1)

    return alias_numbers


def get_customer_id(access_token: str, i_account: int) -> int:
    """Get info of customer that the i_account belongs to.

    :param access_token: Token required to make API calls to the Porta One platform.
    :param i_account: Unique identifier of the pilot account.
    :return: Name of customer.
    """
    get_account_info_url = "/Account/get_account_info"
    get_account_info_header = {"Authorization": f"Bearer {access_token}"}
    get_account_info_body = {
        "params": {
            "i_account": i_account
        }
    }

    t1_start = process_time()
    response = requests.post(get_account_info_url, headers=get_account_info_header,
                             json=get_account_info_body, verify=False)
    t1_stop = process_time()
    turnaround_time = round((t1_stop - t1_start) * 1000)

    print(response.status_code)
    print(turnaround_time)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    i_customer = response.json()["account_info"]["i_customer"]

    logger.info(f"Retrieved customer id of account {i_account}: {i_customer}")
    return i_customer


def setup_trunk_alias(access_token: str, i_account: int, alias_numbers: list[int]) -> bool:
    """Adds alias numbers to pilot account on the Porta One platform.

    :param access_token: Token required to make API calls to the Porta One platform.
    :param i_account: Unique identifier of the pilot account.
    :param alias_numbers: List of numbers to be added as aliases to the pilot account.
    :return: List of account ids of the alias.
    """
    for number in alias_numbers:
        # region Assign DID to account
        add_account_did_url = "/DID/assign_did_to_account"
        add_account_did_header = {"Authorization": f"Bearer {access_token}"}
        add_account_did_body = {
            "params": {
                "i_did_number": number,  # The unique ID of the DID number record
                "i_master_account": i_account  # The unique ID of the account this DID number is assigned to
            }
        }

        t1_start = process_time()
        add_account_did_response = requests.post(add_account_did_url,
                                                 json=add_account_did_body,
                                                 headers=add_account_did_header, verify=False)
        t1_stop = process_time()
        turnaround_time = round((t1_stop - t1_start) * 1000)
        print(add_account_did_response.json())
        print(
            f'Assign DID response:  response_code={add_account_did_response.status_code}, turnaround_time: '
            f'{turnaround_time}ms')

        if add_account_did_response.status_code == 500:
            logger.error("An Error Occurred: " + str(add_account_did_response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        logger.info(f"DID {number} assigned to trunk account {i_account}")
        # endregion

    logger.info(f"All DIDs assigned to trunk account {i_account}")
    return True


def get_DIDs(access_token: str, i_account: int, alias_numbers: list[str]) -> list[int]:
    """Add DIDs to the Porta One Platform and the customer that the given i_account belongs too.

    :param access_token: Token required to make API calls to the Porta One platform.
    :param i_account: Unique identifier of the pilot account.
    :param alias_numbers: Alias numbers to added as DIDs.
    :return: True if all DIDs are added successfully.
    """
    site_id = get_customer_id(access_token, i_account)
    i_did_list = get_i_did_list(access_token, site_id, alias_numbers)
    return i_did_list


def get_i_did_list(access_token: str, i_customer: int, alias_numbers: list[str]) -> list[int]:
    """Gets DIDs from Porta One platform.

    :param access_token: Required to make API calls to Porta One platform.
    :param i_customer: ID of customer that the DID will be assigned to.
    :param alias_numbers: Alias numbers to added as DIDs.
    :return: List of unique identifiers of DIDs to be added.
    """
    did_list: list[dict] = []
    offset = 0
    limit = 100

    add_did_api_url = "/DID/get_number_list"
    add_did_headers = {"Authorization": f"Bearer {access_token}"}
    while True:
        add_did_body = {
            "params": {
                "i_customer": i_customer,
                "usage": "R",
                "offset": offset,
                "limit": limit
            }
        }

        t1_start = process_time()
        response = requests.post(add_did_api_url, json=add_did_body,
                                 headers=add_did_headers, verify=False)
        t1_stop = process_time()
        turnaround_time = round((t1_stop - t1_start) * 1000)

        print(
            f'response_code={response.status_code}, '
            f'turnaround_time: {turnaround_time}ms')

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        if not response.json()["number_list"]:
            break

        did_list.extend(response.json()["number_list"])
        offset += limit

    logger.info("All DIDs retrieved.")

    alias_i_did_list: list[int] = []
    for number in alias_numbers:
        match = False
        for did in did_list:
            if number == did["number"]:
                alias_i_did_list.append(did["i_did_number"])
                match = True
                break
        if not match:
            logger.info(f"{number} was not found in the list of DIDs assigned to customer {i_customer}.")

    logger.info(f"List of DID to be assigned to trunk retrieved.")
    return alias_i_did_list


def assign_did_to_customer(access_token: str, i_customer: int, i_did_list: list[int]) -> bool:
    """Assign DIDs to customer that the account i_account belongs to.

    :param access_token: Required to make API calls to Porta One platform.
    :param i_customer: Unique identifier of the customer.
    :param i_did_list: List of unique identifiers of DIDs to be assigned.
    :return: True if all numbers were successfully assigned.
    """
    for i_did in i_did_list:
        assign_did_api_url = "/DID/assign_did_to_customer"
        assign_did_headers = {"Authorization": f"Bearer {access_token}"}
        assign_did_body = {
            "params": {
                "i_customer": i_customer,
                "i_did_number": i_did
            }
        }

        t1_start = process_time()
        alias_response = requests.post(assign_did_api_url, json=assign_did_body,
                                       headers=assign_did_headers, verify=False)
        t1_stop = process_time()
        turnaround_time = round((t1_stop - t1_start) * 1000)

        print(
            f'Create Account:  response_code={alias_response.status_code}, '
            f'turnaround_time: {turnaround_time}ms')

        if alias_response.status_code == 500:
            logger.error("An Error Occurred: " + str(alias_response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        logger.info(f"DID with id {i_did} added to customer {i_customer}.")

    logger.info(f"All DIDs added to customer {i_customer}")
    return True


def main():
    access_token = get_access_token(USERNAME, TOKEN)

    i_account = -1
    try:
        i_account = int(input("Please enter the i_account of the pilot account: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    alias_numbers = get_alias_numbers()
    logger.info("Alias numbers retrieved.")

    i_did_list = get_DIDs(access_token, i_account, alias_numbers)

    setup_trunk_alias(access_token, i_account, i_did_list)

    input("Operation Done.")


if __name__ == "__main__":
    main()
