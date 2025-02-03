import csv
import logging
import os
import sys
import uuid
import re

from getpass import getpass

import requests

from datetime import datetime
from dotenv import load_dotenv
from time import process_time
from tkinter import filedialog

URL = "/"

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = "Add_DID_Range_" + str(log_time)
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


def get_dids(token: str, i_customer: int) -> list[str]:
    """Gets a list of DIDs for a specific character.

    :param token:
    :param i_customer:
    :return:
    """

    did_list: list[str] = []
    limit = 100
    offset = 0

    did_url = URL + "DID/get_number_list"
    did_header = {"Authorization": f"Bearer {token}"}
    while True:
        did_body = {
            "params": {
                "i_customer": i_customer,
                "offset": offset,
                "limit": limit
            }
        }

        response = requests.post(url=did_url, headers=did_header, json=did_body, verify=False)
        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        if not response.json()["number_list"]:
            break

        offset += limit
        did_list.extend([did["number"] for did in response.json()["number_list"]])

    return did_list


def check_number_format(did: str) -> bool:
    """Checks the format of the provided phone number.

    :param did:
    :return:
    """

    did = did.replace(" ", "")

    if not re.match(r'^27[0-9]{9}$', did):
        logger.error(
            f"An Error Occurred: {did} is not in valid number format."
            f" Phone number needs to start with '27' followed by 9 "
            f"numbers (for example: 27123456789)")
        input(
            f"An Error Occurred: {did} is not in valid number format."
            f" Phone number needs to start with '27' followed by 9 "
            f"numbers (for example: 27123456789)")
        sys.exit(1)

    return True


def compare_dids(did_range: list[int], did_list: list[str]) -> list[int]:
    """

    :return:
    """
    did_list = [int(did) for did in did_list]

    for did in did_list:
        try:
            did_range.remove(did)
            logger.info(f"{did} already loaded for customer.")
        except ValueError:
            logger.info(f"{did} not in range.")

    logger.info("Determined DIDs to be added.")
    return did_range


def add_dids_to_customer(token: str, i_customer: int, did_range: list[int]) -> list[int]:
    """

    :param token:
    :param i_customer:
    :param did_range:
    :return:
    """

    site_name = get_customer_name(token, i_customer)
    i_did_list: list[int] = []

    for did in did_range:
        did = str(did)
        i_group = 35
        for numRange in ["2710133", "2712133", "2713133", "2714133", "2721133",
                         "2731393", "2741133", "2751133", "2787463", "2786"]:
            range_index = did.find(numRange)
            if range_index == 0:
                i_group = 24

        add_did_api_url = "/DID/add_number"
        add_did_headers = {"Authorization": f"Bearer {token}"}
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
                    "vendor_batch_name": "",
                    "external": 1,
                    "free_of_charge": "N",
                    "i_customer": i_customer,
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
                    "number": did
                    # //this is the actual DID number is 164 format I want to variable this from CSV
                }
            }
        }

        response = requests.post(url=add_did_api_url, headers=add_did_headers, json=add_did_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        i_did_list.append(response.json()["i_did_number"])

        assign_did_api_url = "/DID/assign_did_to_customer"
        assign_did_headers = {"Authorization": f"Bearer {token}"}
        assign_did_body = {
            "params": {
                "i_customer": i_customer,
                "i_did_number": response.json()["i_did_number"]
            }
        }

        response = requests.post(url=assign_did_api_url, headers=assign_did_headers, json=assign_did_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        logger.info(f"{did} added to customer {i_customer}.")

    logger.info(f"DIDs added to customer {i_customer}")
    return i_did_list


def get_customer_name(token: str, i_customer: int) -> str:
    """

    :param token:
    :param i_customer:
    :return:
    """
    get_customer_info_url = URL + "Customer/get_customer_info"
    get_customer_info_header = {"Authorization": f"Bearer {token}"}
    get_customer_info_body = {
        "params": {
            "i_customer": i_customer
        }
    }

    response = requests.post(url=get_customer_info_url, headers=get_customer_info_header, json=get_customer_info_body,
                             verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    return response.json()["customer_info"]["name"]


def add_DIDs_to_trunk(token: str, i_account: int, did_range: list[int]) -> bool:
    """

    :param token:
    :param i_account:
    :param did_range:
    :return:
    """
    for did in did_range:
        add_account_did_url = "/DID/assign_did_to_account"
        add_account_did_header = {"Authorization": f"Bearer {token}"}
        add_account_did_body = {
            "params": {
                "i_did_number": did,  # The unique ID of the DID number record
                "i_master_account": i_account  # The unique ID of the account this DID number is assigned to
            }
        }

        response = requests.post(url=add_account_did_url, headers=add_account_did_header, json=add_account_did_body,
                                 verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        logger.info(f"DID {did} added to trunk account {i_account}")

    logger.info(f"All DIDs added to trunk {i_account}")
    return True


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")
    token = get_access_token(usern, passw)

    try:
        i_customer = int(input("Customer id: "))

        did_start = input("DID range start: ")
        check_number_format(did_start)

        did_end = input("DID range end: ")
        check_number_format(did_end)

        did_range = [x for x in range(int(did_start), int(did_end) + 1)]

    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    did_list = get_dids(token, i_customer)
    did_range = compare_dids(did_range, did_list)
    i_did_list = add_dids_to_customer(token, i_customer, did_range)

    if input("Add DIDs to trunk? (No/Yes): ") == "Yes":
        try:
            i_acc = int(input("Please provide trunk account unique ID: "))
        except ValueError as e:
            logger.error("An Error Occurred: " + str(e))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        add_DIDs_to_trunk(token, i_acc, i_did_list)

    logger.info("Operation Complete.")
    input("Operation Complete.")
    sys.exit(0)


if __name__ == "__main__":
    main()
