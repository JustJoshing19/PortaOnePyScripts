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
logging_name = "Move_DID_Trunk_To_Sips_" + str(log_time)
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


def get_extension_dids() -> list[dict[str, str]]:
    """

    :return:
    """
    ext_did_list: list[dict[str, str]] = []

    with open(filedialog.askopenfilename(), "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for data in csv_reader:
            data: dict
            ext_did_list.append({data["ext"]: data["did"]})

    return ext_did_list


def get_trunk_alias(token: str, i_account: int) -> list[dict]:
    """

    :param token:
    :param i_account:
    :return:
    """
    alias_list: list[dict] = []
    offset = 0
    limit = 300
    get_alias_list_url = URL + "Account/get_alias_list"
    get_alias_list_header = {"Authorization": f"Bearer {token}"}
    while True:
        get_alias_list_body = {
            "params": {
                "check_did": 1,
                "get_total": 1,
                "i_master_account": i_account,
                "id": "27%",
                "limit": limit,
                "offset": offset
            }
        }

        response = requests.post(url=get_alias_list_url, headers=get_alias_list_header, json=get_alias_list_body,
                                 verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        if not response.json()["alias_list"]:
            break

        offset += limit
        alias_list.extend(response.json()["alias_list"])

    logger.info(f"All DID alias found for Trunk account {i_account}.")
    return alias_list


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


def compare_dids(alias_list: list[dict], acc_list: list[dict], ext_did_list: list[dict[str, str]]) -> list[list[int|str]]:
    """

    :param acc_list:
    :param alias_list:
    :param ext_did_list:
    :return:
    """
    finding_results = {
        0: "BOTH FOUND",
        1: "DID NOT FOUND",
        2: "EXT NOT FOUND",
        3: "NONE FOUND"
    }
    found_list: list[list[int]] = []
    csv_result_list: list[dict[str, str]] = []
    csv_name = f"DID_Extension_Search_Result_{str(log_time)}.csv"
    for ext_did in ext_did_list:
        result = 3
        found_entry: list[int | str] = []
        file_ext_num = list(ext_did.keys())[0]
        file_did_num = list(ext_did.values())[0]
        for did in alias_list:
            if file_did_num == did["id"]:
                result -= 1
                found_entry.append(did["i_account"])
                found_entry.append(did["i_did_number"])
                found_entry.append(did["id"])
                break

        for acc in acc_list:
            extension_num = str(acc["id"]).split("x")
            if file_ext_num == extension_num[-1]:
                result -= 2
                found_entry.append(acc["i_account"])
                break

        csv_result_list.append({
            "extension": file_ext_num,
            "DID": file_did_num,
            "finding_result": finding_results[result]
        })

        match result:
            case 0:
                found_list.append(found_entry)
            case 1:
                logger.info(
                    f"{finding_results[result]}: DID {file_did_num} was not found under the provided trunk account.")
            case 2:
                logger.info(
                    f"{finding_results[result]}: Extension {file_ext_num} was not found under given customer site.")
            case 3:
                logger.info(
                    f"{finding_results[result]}: DID {file_did_num} was not found under the provided trunk account and "
                    f"Extension {file_ext_num} was not found under given customer site.")

    with open(csv_name, "a", newline="") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=list(csv_result_list[0].keys()))
        csv_writer.writeheader()
        csv_writer.writerows(csv_result_list)

    logger.info(f"DIDs and Extension search result writen to CSV '{csv_name}'")

    return found_list


def move_did(token: str, did_i_acc: int, i_did_number: int, sip_i_acc: int, did_id: str, i_customer: int) -> bool:
    """

    :param did_id:
    :param i_customer:
    :param token:
    :param did_i_acc:
    :param i_did_number:
    :param sip_i_acc:
    :return:
    """
    release_did_url = URL + "Account/delete_alias"
    release_did_header = {"Authorization": f"Bearer {token}"}
    release_did_body = {
        "params": {
            "alias_info": {
                "i_account": did_i_acc
            },
            "release_assigned_did": 1
        }
    }

    response = requests.post(url=release_did_url, headers=release_did_header, json=release_did_body, verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        sys.exit(1)

    logger.info(f"Alias removed from trunk.")

    assign_customer_did_url = URL + "DID/assign_did_to_customer"
    assign_customer_did_header = {"Authorization": f"Bearer {token}"}
    assign_customer_did_body = {
        "params": {
            "i_customer": i_customer,
            "i_did_number": i_did_number
        }
    }

    response = requests.post(url=assign_customer_did_url, headers=assign_customer_did_header,
                             json=assign_customer_did_body, verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    logger.info(f"DID, with id {i_did_number}, assigned to customer {i_customer}.")

    assign_account_did_url = URL + "DID/assign_did_to_account"
    assign_account_did_header = {"Authorization": f"Bearer {token}"}
    assign_account_did_body = {
        "params": {
            "i_master_account": sip_i_acc,
            "i_did_number": i_did_number
        }
    }

    response = requests.post(url=assign_account_did_url, headers=assign_account_did_header,
                             json=assign_account_did_body, verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    logger.info(f"DID, with id {i_did_number}, assigned to account {sip_i_acc}.")
    logger.info(f"DID Movement Complete.")

    update_account_services_info_url = "/Account/update_service_features"
    update_account_services_info_header = {"Authorization": f"Bearer {token}"}
    update_account_services_info_body = {
        "params": {
            "i_account": sip_i_acc,
            "service_features": [{
                "attributes": [
                    {
                        "effective_values": [
                            did_id
                        ],
                        "name": "centrex",
                        "values": [
                            did_id
                        ]
                    },
                    {
                        "effective_values": [
                            ""
                        ],
                        "name": "display_number",
                        "values": [
                            ""
                        ]
                    }
                ],
                "effective_flag_value": "Y",
                "flag_value": "Y",
                "locked": 0,
                "locks": [],
                "name": "cli"
            }]
        }
    }

    response = requests.post(url=update_account_services_info_url, headers=update_account_services_info_header,
                             json=update_account_services_info_body, verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        print("An Error Occurred")
        sys.exit(1)

    logger.info(f"Update identity override for account {sip_i_acc}")

    return True


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    token = get_access_token(usern, passw)
    ext_did_list = get_extension_dids()
    print(ext_did_list)

    try:
        i_account = int(input("Please provide the trunk account's unique numeral id: "))
        i_customer = int(input("Please provide the extensions' customer site unique numeral id: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    alias_list = get_trunk_alias(token, i_account)
    print(alias_list)

    acc_list = get_ph_accounts(token, i_customer, "ph")
    acc_list.extend(get_ph_accounts(token, i_customer, "0"))
    print(acc_list)

    checked_list = compare_dids(alias_list, acc_list, ext_did_list)
    print(checked_list)

    for entry in checked_list:
        move_did(token, entry[0], entry[1], entry[3], entry[2], i_customer)

    input("Operation Complete.")
    sys.exit(0)


if __name__ == "__main__":
    main()
