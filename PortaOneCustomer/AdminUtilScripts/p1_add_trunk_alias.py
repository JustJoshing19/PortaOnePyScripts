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
                alias_numbers.append(row["phoneNumber"])
    except IndexError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An error occurred. Check log.")
        sys.exit(1)

    return alias_numbers


def get_customer_name(access_token: str, i_account: int) -> list[int | str]:
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

    get_customer_info_url = "/Customer/get_customer_info"
    get_customer_info_header = {"Authorization": f"Bearer {access_token}"}
    get_customer_info_body = {
        "params": {
            "i_customer": i_customer
        }
    }

    t1_start = process_time()
    response = requests.post(get_customer_info_url, headers=get_customer_info_header,
                             json=get_customer_info_body, verify=False)
    t1_stop = process_time()
    turnaround_time = round((t1_stop - t1_start) * 1000)

    print(response.status_code)
    print(turnaround_time)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    customer_id_name: list[int | str] = [i_customer, response.json()["customer_info"]["name"]]

    logger.info(f"Retrieved customer id of account {i_account}: {i_customer}")
    return customer_id_name


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

        logger.info(f"DID {number} assigned to master account {i_account}")
        # endregion

    logger.info(f"All DIDs assigned to master account {i_account}")
    return True


def add_DIDs(access_token: str, i_account: int, alias_numbers: list[str]) -> list[int]:
    """Add DIDs to the Porta One Platform and the customer that the given i_account belongs too.

    :param access_token: Token required to make API calls to the Porta One platform.
    :param i_account: Unique identifier of the pilot account.
    :param alias_numbers: Alias numbers to added as DIDs.
    :return: True if all DIDs are added successfully.
    """
    site_id_name = get_customer_name(access_token, i_account)
    i_did_list = add_did_to_porta(access_token, site_id_name[1], alias_numbers)
    assign_did_to_customer(access_token, site_id_name[0], i_did_list)

    logger.info("DIDs have been added.")
    return i_did_list


def add_did_to_porta(access_token: str, site_name: str, alias_numbers: list[str]) -> list[int]:
    """Adds DIDs to Porta One platform.

    :param access_token: Required to make API calls to Porta One platform.
    :param site_name: Name of customer that the DID will be assigned to.
    :param alias_numbers: Alias numbers to added as DIDs.
    :return: List of unique identifiers of added DIDs.
    """
    i_did_list: list[int] = []
    for number in alias_numbers:
        i_group = 35
        for numRange in NUMBER_RANGES:
            range_index = number.find(numRange)
            if range_index == 0:
                i_group = 24

        add_did_api_url = "/DID/add_number"
        add_did_headers = {"Authorization": f"Bearer {access_token}"}
        add_did_body = {
            "params": {
                "number_info": {
                    "activation_cost": 0.0,
                    "activation_fee": 0.0,
                    "activation_revenue": 0.0,
                    "country_iso": "ZA",
                    "country_name": "South Africa",
                    "periodic_fee": 0.0,
                    "recurring_cost": 0.0,
                    "vendor_batch_name": "Gijima SBC Test",
                    "external": 1,
                    "free_of_charge": "N",
                    "i_dv_batch": 114,
                    "i_do_batch": 147,
                    "i_group": i_group,
                    "i_vendor": 152,
                    "is_used": 1,
                    "iso_4217": "ZAR",
                    "frozen": "N",
                    # //variables apply to the below
                    "description": site_name,
                    # // i would like to have the Branchname as the description of the DID
                    #  IE Br_CapeTown_0800 from the csv
                    "number": number
                    # //this is the actual DID number is 164 format I want to variable this from CSV
                }
            }
        }

        t1_start = process_time()
        alias_response = requests.post(add_did_api_url, json=add_did_body,
                                       headers=add_did_headers, verify=False)
        t1_stop = process_time()
        turnaround_time = round((t1_stop - t1_start) * 1000)

        print(
            f'Create Account:  response_code={alias_response.status_code}, '
            f'turnaround_time: {turnaround_time}ms')

        if alias_response.status_code == 500:
            logger.error("An Error Occurred: " + str(alias_response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        i_did = alias_response.json()['i_did_number']
        logger.info(f"Added {number} to Porta DID inventory. ID: {i_did}")

        i_did_list.append(i_did)

    logger.info("All DIDs uploaded.")
    return i_did_list


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

    i_did_list = add_DIDs(access_token, i_account, alias_numbers)

    setup_trunk_alias(access_token, i_account, i_did_list)

    input("Operation Done.")


if __name__ == "__main__":
    main()
