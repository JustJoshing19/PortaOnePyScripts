import json.decoder
import logging
import sys
from datetime import datetime
from getpass import getpass
from time import process_time, sleep

import requests

URL = ""

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = "Delete_Pincodes_" + str(log_time)
logging.basicConfig(filename=logging_name + '.log',
                    filemode='a',
                    format='%(asctime)s, %(msecs)-3d ms || %(name)-22s ' +
                           '%(levelname)-5s ' +
                           '|| %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger("Full Import Logger")


# endregion


def get_access_token(user: str, passw: str) -> str:
    """Get session ID to use for API calls.

    Returns
    -------
        str
            Session ID used for making API calls.
    """
    login_api_url = URL + "Session/login"
    login_body = {
        'params': {
            'login': user,
            'password': passw
        }}

    t1_start = process_time()
    response = requests.post(login_api_url, json=login_body, verify=False)
    t1_stop = process_time()

    turnaround_time = round((t1_stop - t1_start) * 1000)
    print(turnaround_time)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred, Check Log.")
        sys.exit(1)

    logger.info("Access Token Retrieved Successfully.")
    try:
        access_token = response.json()['access_token']
    except json.decoder.JSONDecodeError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log. Please make sure you are not on a VPN.")
        sys.exit(1)

    return access_token


def get_pincode_accounts(token: str, customer: int) -> list[int]:
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
                "id": "PIN_%",
                "limit": limit,
                "offset": offset
            }
        }  # Edit in case of more than 100 Pincodes accounts

        response = requests.post(url=pin_url, headers=pin_header, json=pin_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        try:
            if not response.json()["account_list"]:
                break
        except json.decoder.JSONDecodeError as e:
            logger.error("An Error Occurred: " + str(e))
            input("An Error Occurred. Check Log. Please make sure you are not on a VPN.")
            sys.exit(1)

        offset += limit
        for i_account in response.json()["account_list"]:
            acc_list.append(i_account["i_account"])

    logger.info(f"Pincode Accounts of customer {customer} retrieved successfully.")
    return acc_list


def delete_pin_accs(token: str, acc_list: list[int]) -> bool:
    """

    :param token:
    :param acc_list:
    :return:
    """
    del_pin_url = URL + "Account/terminate_account"
    del_account_header = {"Authorization": f"Bearer {token}"}
    for i_acc in acc_list:
        del_account_body = {
            "params": {
                "i_account": i_acc  # id of account that is going to be deleted.
            }
        }

        response = requests.post(url=del_pin_url, headers=del_account_header, json=del_account_body, verify=False)

        try:
            if response.status_code == 500:
                logger.error("An Error Occurred: " + str(response.json()))
                input("An Error Occurred. Check Log.")
                sys.exit(1)
        except json.decoder.JSONDecodeError as e:
            logger.error("An Error Occurred: " + str(e))
            input("An Error Occurred. Check Log. Please make sure you are not on a VPN.")
            sys.exit(1)

        logger.info(f"Pincode account {i_acc} deleted.")

    return True


def main():
    print("-------------------------------------------------------------------------------------------")
    print("This program will remove all Pincode Accounts and their aliases from a given customers site.")
    print("-------------------------------------------------------------------------------------------")
    print()
    user = input("Please provide username: ")
    password = getpass("Please provide password: ")

    token = get_access_token(user, password)

    try:
        customer = int(input("Please enter customer unique id: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    acc_list = get_pincode_accounts(token, customer)
    print(acc_list)

    confirmation = input(f"Delete pincodes for customer {customer}? (y/n): ")
    if confirmation != "y":
        logger.info(f"Input given {confirmation}")
        logger.info("Pincodes deletion cancelled.")
        input("Canceled Operation.")
        sys.exit(1)

    delete_pin_accs(token, acc_list)
    logger.info(f"All Pincodes for customer {customer} has been terminated.")

    input("All deletions done.")
    sys.exit(0)


if __name__ == "__main__":
    main()
