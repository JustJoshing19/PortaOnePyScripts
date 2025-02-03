import csv
import json.decoder
import logging
import os
import re
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
logging_name = "Update_Account_Simple_Forwarding_" + str(log_time)
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

    try:
        access_token = response.json()['access_token']
    except json.decoder.JSONDecodeError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log. Please make sure you are not on a VPN.")
        sys.exit(1)

    logger.info("Token has been retrieved.")
    return access_token


def get_ph_account_list(session_id: str, i_customer: int) -> list[dict]:
    phacc_list: list[dict] = []
    offset = 0
    limit = 200
    while True:
        list_accounts_url = "/Account/get_account_list"
        list_accounts_header = {"Authorization": f"Bearer {session_id}"}
        list_accounts_body = {
            "params": {
                "bill_status": "O",
                "billing_model": 1,
                "i_customer": i_customer,
                "id": "ph%",
                "offset": offset,
                "limit": limit
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

        try:
            if not response.json()['account_list']:
                break
        except json.decoder.JSONDecodeError as e:
            logger.error("An Error Occurred: " + str(e))
            input("An Error Occurred. Check Log. Please make sure you are not on a VPN.")
            sys.exit(1)

        phacc_list.extend(response.json()['account_list'])
        offset += limit

    return phacc_list


def update_forwarding(session_id: str, acc_list: list[dict], forward_number: str) -> bool:
    for acc in acc_list:
        update_acc_services_info_url = "/Account/update_service_features"
        update_acc_services_info_header = {"Authorization": f"Bearer {session_id}"}
        update_acc_services_info_body = {
            "params": {
                "i_account": acc["i_account"],
                "service_features": [
                    {
                        "effective_flag_value": "C",
                        "flag_value": "C",
                        "locked": 0,
                        "locks": [

                        ],
                        "name": "forward_mode"
                    }
                ]
            }
        }

        t1_start = process_time()
        response = requests.post(update_acc_services_info_url, headers=update_acc_services_info_header,
                                 json=update_acc_services_info_body, verify=False)
        t1_stop = process_time()
        turnaround_time = round((t1_stop - t1_start) * 1000)

        print(response.status_code)
        print(turnaround_time)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        try:
            response.json()
        except json.decoder.JSONDecodeError as e:
            logger.error("An Error Occurred: " + str(e))
            input("An Error Occurred. Check Log. Please make sure you are not on a VPN.")
            sys.exit(1)

        logger.info(f'Account {acc["i_account"]} default mode updated to "Forward Only"')

        get_account_info_url = "/Account/add_followme_number"
        get_account_info_header = {"Authorization": f"Bearer {session_id}"}
        get_account_info_body = {
            "params": {
                "number_info": {
                    "active": "Y",
                    "i_account": acc["i_account"],
                    "i_follow_order": 1,
                    "keep_original_cli": "Y",
                    "redirect_number": f'{forward_number}',
                    "timeout": 15,
                    "use_tcp": "N",
                    "weight": 0.0
                }
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

        try:
            response.json()
        except json.decoder.JSONDecodeError as e:
            logger.error("An Error Occurred: " + str(e))
            input("An Error Occurred. Check Log. Please make sure you are not on a VPN.")
            sys.exit(1)

        logger.info(f'Account {acc["i_account"]} simple forwarding updated.')

    logger.info(f'All accounts forwarding updated.')
    return True


def get_exception_list(acc_list: list[dict]) -> list[dict]:
    f_location = filedialog.askopenfilename()
    except_list: list[str] = []
    with open(f_location, "r") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for ext in csv_reader:
            ext: dict
            except_list.append(ext["extension"])

    allowed_list = acc_list
    for i in range(len(acc_list) - 1, - 1, -1):
        try:
            if acc_list[i]["extension_id"] in except_list:
                acc_list.pop(i)
        except IndexError as e:
            print(str(e))

    return acc_list


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    token = get_access_token(usern, passw)

    try:
        i_customer = int(input("Customer ID: "))
        forward_number = input("Please enter the number to forward to: ")
        if not re.match(r"^27[0-9]{9}$", forward_number):
            logger.error("An Error Occurred: No forward number given.")
            input("An Error Occurred. Check Log.")
            sys.exit(1)

    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    acc_list = get_ph_account_list(token, i_customer)
    if input("Do you have an extension exception CSV file?(y/n): ") == 'y':
        acc_list = get_exception_list(acc_list)

    update_forwarding(token, acc_list, forward_number)

    logger.info("Operation Complete.")
    input("Operation Complete.")
    sys.exit(0)


if __name__ == "__main__":
    main()
