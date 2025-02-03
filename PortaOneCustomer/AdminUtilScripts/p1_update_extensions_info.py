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
USERNAME = os.getenv("USER")
URL = os.getenv("URL")

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = "Update_Extension_" + str(log_time)
logging.basicConfig(filename=logging_name + '.log',
                    filemode='a',
                    format='%(asctime)s, %(msecs)-3d ms || %(name)-22s ' +
                           '%(levelname)-5s ' +
                           '|| %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger("Full Import Logger")


# endregion
def get_access_token() -> str:
    """Get session ID to use for API calls.

    Returns
    -------
        str
            Session ID used for making API calls.
    """
    login_api_url = URL + "Session/login"
    login_body = {
        'params': {
            'login': USERNAME,
            'token': TOKEN
        }}

    t1_start = process_time()
    response = requests.post(login_api_url, json=login_body, verify=False)
    t1_stop = process_time()

    turnaround_time = round((t1_stop - t1_start) * 1000)
    print(turnaround_time)
    print(response.status_code)

    access_token = response.json()['access_token']

    logger.info("Access Token received.")
    return access_token


def get_extension_update_data(file_location: str) -> list[dict]:
    """

    :param file_location: Path to file.
    :return:
    """
    ext_data_list: list[dict] = []
    try:
        with open(file_location, "r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for data in csv_reader:
                data: dict
                ext_data_list.append(data)
    except FileNotFoundError as e:
        logger.error("An Error Occurred: " + str(e))

    logger.info("Retrieved Extension Update Data from csv file.")
    return ext_data_list


def update_pbx_ext(token: str, update_body: dict) -> bool:
    """

    :param token:
    :param update_body:
    :return:
    """
    ext_update_url = URL + "Customer/update_customer_extension"
    ext_update_header = {"Authorization": f"Bearer {token}"}
    ext_update_body = {
        "params": update_body
    }

    response = requests.post(url=ext_update_url, headers=ext_update_header, json=ext_update_body, verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    i_c_ext = response.json()["i_c_ext"]
    logger.info(f"Updated PBX extension: {i_c_ext}")
    return True


def update_sip_account(token: str, update_body: dict) -> bool:
    """

    :param token:
    :param update_body:
    :return:
    """
    sip_update_url = URL + "Account/update_account"
    sip_update_header = {"Authorization": f"Bearer {token}"}
    sip_update_body = {
        "params": update_body
    }

    response = requests.post(url=sip_update_url, headers=sip_update_header, json=sip_update_body, verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    i_account = response.json()["i_account"]
    logger.info(f"Updated account: {i_account}")
    return True


def get_i_c_ext(token: str, i_customer: int) -> list[dict]:
    """

    :param i_customer:
    :param token:
    :return:
    """
    i_c_ext_url = URL + "Customer/get_extensions_list"
    i_c_ext_header = {"Authorization": f"Bearer {token}"}
    i_c_ext_body = {
        "params": {
            "i_customer": i_customer
        }
    }

    response = requests.post(url=i_c_ext_url, headers=i_c_ext_header, json=i_c_ext_body, verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    logger.info(f"Retrieved extension list from i_customer {i_customer}")
    return response.json()["extensions_list"]


def get_customer(token: str, i_account: int) -> int:
    """

    :param token:
    :param i_account:
    :return:
    """
    cust_url = URL + "Account/get_account_info"
    cust_header = {"Authorization": f"Bearer {token}"}
    cust_body = {
        "params": {
            "i_account": i_account
        }
    }

    response = requests.post(url=cust_url, headers=cust_header, json=cust_body, verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    i_customer = response.json()["account_info"]["i_customer"]
    logger.info(f"Received i_customer: {i_customer}")
    return i_customer


def update_information(token: str, ext_data_file: list[dict]) -> bool:
    """

    :param token:
    :param ext_data_file:
    :return:
    """

    for data in ext_data_file:
        i_customer = get_customer(token, data["i_account"])
        i_c_ext_list = get_i_c_ext(token, i_customer)

        i_c_ext = 0
        for ext in i_c_ext_list:
            if ext["i_account"] == data["i_account"]:
                i_c_ext = ext["i_c_ext"]
                logger.info(f"Retrieved i_c_ext: {i_c_ext}")

        sip_body = {
            "account_info": {
                "firstname": data["firstname"],
                "lastname": data["lastname"]
            }
        }
        update_sip_account(token, sip_body)

        ext_body = {
            "i_c_ext": i_c_ext,
            "name": f'{data["firstname"].data["lastname"]}'
        }
        update_pbx_ext(token, ext_body)

        ecn_prov = [{"i_customer": i_customer,
                     "line_number": 1,
                     "ext_number": "",
                     "mac_address": "",
                     "display_name_first": f"{data['firstname']}",
                     "display_name_last": f"{data['lastname']}",
                     "i_model": 0,
                     "porta_user": "Gijima",
                     "action": "add"}]

        logger.info(f"All SIP, PBX and ECN data updated.")

    logger.info("All extension data updated.")
    return True


def main():
    token = get_access_token()

    file_location = filedialog.askopenfilename(defaultextension=".csv")
    if (not file_location) or (file_location[-4:] != ".csv"):
        logger.error("File was not selected or had incorrect extension.")
        sys.exit()
    logger.info(f"Received file location: {file_location}")

    ext_data_file = get_extension_update_data(file_location)
    update_information(token, ext_data_file)

    logger.info("Operation Complete.")
    input("Operation Complete.")
    sys.exit(0)


if __name__ == "__main__":
    main()
