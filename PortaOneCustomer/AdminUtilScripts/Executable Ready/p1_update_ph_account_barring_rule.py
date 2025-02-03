import json.decoder
import logging
import sys
from datetime import datetime
from getpass import getpass
from time import process_time

import requests

URL = ""

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = "Barring_Rule_Update_" + str(log_time)
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

    try:
        access_token = response.json()['access_token']
    except json.decoder.JSONDecodeError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log. Please make sure you are not on a VPN.")
        sys.exit(1)

    logger.info("Access Token Retrieved Successfully.")

    return access_token


def get_ph_accounts(access_token: str, i_customer: int) -> list[int]:
    """

    :param access_token:
    :param i_customer:
    :return:
    """
    limit = 200
    offset = 0

    ph_url = URL + "Account/get_account_list"
    ph_header = {"Authorization": f"Bearer {access_token}"}
    i_account_list: list[int] = []

    while True:
        ph_body = {
            "params": {
                "bill_status": "O",
                "billing_model": 1,
                "i_customer": i_customer,
                "id": "ph%",
                "offset": offset,
                "limit": limit
            }
        }

        response = requests.post(url=ph_url, headers=ph_header, json=ph_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))

        try:
            response.json()
        except json.decoder.JSONDecodeError as e:
            logger.error("An Error Occurred: " + str(e))
            input("An Error Occurred. Check Log. Please make sure you are not on a VPN.")
            sys.exit(1)

        for data in response.json()["account_list"]:
            i_account_list.append(data["i_account"])

        if not response.json()["account_list"]:
            break

        offset += limit

    return i_account_list


def update_accounts(access_token: str, i_account_list: list[int], activate_barring: bool) -> bool:
    """

    :param access_token:
    :param activate_barring:
    :param i_account_list:
    :return:
    """
    update_acc_url = URL + "Account/update_account"
    update_acc_header = {"Authorization": f"Bearer {access_token}"}

    flag_value = "N"
    call_barring_rule_id = ""
    if activate_barring:
        flag_value = "Y"
        call_barring_rule_id = "1758"
    for i_account in i_account_list:

        update_acc_body = {
            "params": {
                "account_info": {
                    "i_account": i_account,
                    "service_features": [
                        {
                            "attributes": [
                                {
                                    "effective_values": [
                                        call_barring_rule_id
                                    ],
                                    "name": "call_barring_rules",
                                    "values": [
                                        call_barring_rule_id
                                    ]
                                }
                            ],
                            "effective_flag_value": flag_value,
                            "flag_value": flag_value,
                            "locked": 0,
                            "locks": [
                                "user"
                            ],
                            "name": "call_barring"
                        }
                    ]}
            }
        }

        response = requests.post(url=update_acc_url, headers=update_acc_header, json=update_acc_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            sys.exit(1)

        try:
            response.json()
        except json.decoder.JSONDecodeError:
            logger.error("An Error Occurred: " + str(e))
            input("An Error Occurred. Check Log. Please make sure you are not on a VPN.")
            sys.exit(1)

        logger.info(f"i_account {i_account} services updated.")

    return True


def main():
    print("-------------------------------------------------------------------------------------------")
    print("This program will enable/disable call barring on all ph Accounts on a customer site.")
    print("-------------------------------------------------------------------------------------------")
    print()
    user = input("Please provide username: ")
    password = getpass("Please provide password: ")

    token = get_access_token(user, password)

    try:
        i_customer = int(input("Please enter the unique customer id: "))
        on_off = input("Turn Barring Rules (On) Or (Off): ")
        on_off = on_off.lower()

        if on_off == "on":
            activate_barr = True
        elif on_off == "off":
            activate_barr = False
        else:
            logger.info(f"No Valid Input Given. ({on_off})")
            input(f"No Valid Input Given. ({on_off})\n"
                  f"Please provide either 'On' or 'Off'.")
            sys.exit(1)
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        sys.exit(1)

    i_account_list = get_ph_accounts(token, i_customer)
    logger.info("List of account id's for customer " + str(i_customer) + " retrieved: " + str(i_account_list))

    update_accounts(token, i_account_list, activate_barr)
    logger.info(f"Customer {i_customer} account's barring rules updated. ({on_off})")
    input(f"Customer {i_customer} account's barring rules updated. ({on_off})")
    sys.exit(0)


if __name__ == "__main__":
    main()
