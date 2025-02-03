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
logging_name = "Update_IVRs_" + str(log_time)
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
    """

    :param usern:
    :param passw:
    :return:
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


def get_accounts(token: str, customer: int) -> list[int]:
    """

    :param token:
    :param customer:
    :return:
    """
    acc_list: list[int] = []
    limit = 200
    offset = 0
    pin_url = URL + "Account/get_account_list"
    pin_header = {"Authorization": f"Bearer {token}"}

    while True:
        pin_body = {
            "params": {
                "bill_status": "O",
                "i_customer": f"{customer}",
                "billing_model": 1,
                "id": "ph%",
                "limit": limit,
                "offset": offset
            }
        }  # Edit in case of more than 100 Pincodes accounts

        response = requests.post(url=pin_url, headers=pin_header, json=pin_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            sys.exit(1)

        if not response.json()["account_list"]:
            break

        for i_account in response.json()["account_list"]:
            acc_list.append(i_account["i_account"])

        offset += limit

    logger.info("Accounts retrieved.")
    return acc_list


def update_acc(session_id: str, account_did: list[int]) -> bool:
    """

    :param session_id:
    :param account_did:
    :return:
    """
    flag_value = "Y"
    flag_input = input("Turn IVR (on) or (off): ")
    match flag_input.lower():
        case "on":
            pass
        case "off":
            flag_value = "N"
        case _:
            logger.info("Incorrect input was given.")
            input("Incorrect input was given.")
            sys.exit(1)

    for acc in account_did:
        update_account_info_url = "/Account/update_account"
        update_account_info_header = {"Authorization": f"Bearer {session_id}"}
        update_account_info_body = {
            "params": {
                "account_info": {
                    "i_account": acc,
                    "service_features": [{
                        "attributes": [
                            {
                                "effective_values": [
                                    ""
                                ],
                                "name": "outgoing_access_number",
                                "values": [
                                    ""
                                ]
                            }
                        ],
                        "effective_flag_value": flag_value,
                        "flag_value": flag_value,
                        "locked": 0,
                        "locks": [
                            "user"
                        ],
                        "name": "voice_pass_through"
                    }]
                }
            }
        }

        t1_start = process_time()
        response = requests.post(update_account_info_url, headers=update_account_info_header,
                                 json=update_account_info_body, verify=False)
        t1_stop = process_time()
        turnaround_time = round((t1_stop - t1_start) * 1000)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            print("An Error Occurred")
            sys.exit(1)

        print(response.status_code)
        print(turnaround_time)

        logger.info(f"Account {acc} IVR Services Updated.")

    logger.info("All Account IVR Services Updated")
    return True


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    token = get_access_token(usern, passw)

    try:
        i_customer = int(input("Provide customers id: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    acc_list = get_accounts(token, i_customer)
    update_acc(token, acc_list)

    logger.info("Script Finished.")
    input("Script Finished.")
    sys.exit(0)


if __name__ == "__main__":
    main()
