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
logging_name = "p1_update_RTP_proxy_Email_Login_Clinix_" + str(log_time)
logging.basicConfig(filename=logging_name + '.log',
                    filemode='a',
                    format='%(asctime)s, %(msecs)-3d ms || %(name)-22s ' +
                           '%(levelname)-5s ' +
                           '|| %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.NOTSET)
logger = logging.getLogger("Full Import Logger")


# endregion


def get_ph_accounts(token: str, i_customer: int, sip_prefix="ph") -> list[dict]:
    """

    :param i_customer:
    :param sip_prefix:
    :param token:
    :return:
    """
    i_acc_list: list[dict] = []
    limit = 100
    offset = 0
    get_ph_accounts_url = URL + "Account/get_account_list"
    get_ph_accounts_header = {"Authorization": f"Bearer {token}"}
    while True:
        get_ph_accounts_body = {
            "params": {
                "bill_status": "O",
                "i_customer": i_customer,
                "billing_model": 1,
                "id": (sip_prefix + "%"),
                "limit": limit,
                "offset": offset
            }
        }

        response = requests.post(url=get_ph_accounts_url, headers=get_ph_accounts_header, json=get_ph_accounts_body,
                                 verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        if not response.json()["account_list"]:
            break

        offset += limit
        i_acc_list.extend(response.json()["account_list"])

    logger.info(f"Retrieved Accounts from Customer {i_customer}")
    return i_acc_list


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


def compare_file_accs(site_accs: list[dict]) -> list[dict]:
    """

    :param site_accs:
    :return:
    """
    match_list: list[dict] = []
    file_acc_id_list: list[dict] = []
    with open(filedialog.askopenfilename(), "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for acc in csv_reader:
            acc: dict
            file_acc_id_list.append(acc)

    for f_acc in file_acc_id_list:
        found = False
        for s_acc in site_accs:
            if str(s_acc['id']).split("x")[-1] == f_acc["id"]:
                s_acc["email"] = f_acc["email"]
                match_list.append(s_acc)
                found = True
                break

        if not found:
            logger.info(f"Extension {f_acc['id']} was not found.")

    return match_list


def update_acc_proxy(token: str, match_list: list[dict]) -> bool:
    """

    :param token:
    :param match_list:
    :return:
    """
    sip_account_password = uuid.uuid4()
    sip_account_password = str(sip_account_password)[:15]
    update_account_services_info_url = "/Account/update_account"
    update_account_services_info_header = {"Authorization": f"Bearer {token}"}
    for acc in match_list:
        update_account_services_info_body = {
            "params": {
                "account_info": {
                    "i_account": acc["i_account"],
                    "email": acc["email"],
                    "i_product": 30303,
                    "login": f"{acc['firstname']}.{acc['lastname']}",
                    "password": sip_account_password,
                    "service_features": [
                        {
                            "attributes": [

                            ],
                            "effective_flag_value": "3",
                            "flag_value": "3",
                            "locked": 0,
                            "locks": [

                            ],
                            "name": "rtpp_level"
                        }
                    ]
                }
            }
        }

        response = requests.post(url=update_account_services_info_url, headers=update_account_services_info_header,
                                 json=update_account_services_info_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            print("An Error Occurred")
            sys.exit(1)

        logger.info(f"Updated RTP Proxy for account {acc['i_account']}")
    return True


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    token = get_access_token(usern, passw)

    try:
        i_customer = int(input("Please provide the extensions' customer site unique numeral id: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    site_acc_list = get_ph_accounts(token, i_customer, "ph")
    match_list = compare_file_accs(site_acc_list)
    update_acc_proxy(token, match_list)


if __name__ == "__main__":
    main()
