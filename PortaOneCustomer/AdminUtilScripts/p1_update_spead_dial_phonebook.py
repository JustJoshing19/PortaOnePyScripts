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
logging_name = "Update_Phonebook_speed_dials_" + str(log_time)
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


def get_customer_name(token: str, i_customer: int) -> str:
    """

    :param token:
    :param i_customer:
    :return:
    """
    cust_name_url = URL + "Customer/get_customer_info"
    cust_name_header = {"Authorization": f"Bearer {token}"}
    cust_name_body = {
        "params": {
            "i_customer": i_customer
        }
    }

    response = requests.post(url=cust_name_url, headers=cust_name_header, json=cust_name_body, verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    return response.json()["customer_info"]["name"]


def get_speed_dials(token: str, i_customer: int, site_name: str) -> list[dict]:
    """

    :param token:
    :param i_customer:
    :param site_name:
    :return:
    """
    limit = 100
    offset = 0
    speed_dial_list = []

    speed_dial_url = URL + "Customer/get_abbreviated_dialing_number_list"
    speed_dial_header = {"Authorization": f"Bearer {token}"}
    while True:
        speed_dial_body = {
            "params": {
                "i_customer": i_customer,
                "limit": limit,
                "offset": offset
            }
        }

        response = requests.post(url=speed_dial_url, headers=speed_dial_header, json=speed_dial_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        if not response.json()["abbreviated_dialing_number_list"]:
            break

        offset += limit
        speed_dial_list.extend([{
            "display_name": dial["description"],
            "office_number": dial["abbreviated_number"],
            "mobile_number": "",
            "other_number": "",
            "line": -1,
            "ring": "auto",
            "auto_divert": "",
            "priority": "",
            "group_id_name": site_name}
            for dial in response.json()["abbreviated_dialing_number_list"]])

    logger.info(f"All speed dials retrieved from customer {site_name}, {i_customer}")
    return speed_dial_list


def save_to_csv(ext_list: list[dict]) -> bool:
    """

    :param ext_list:
    :return:
    """

    new_f = True if input("Add site to existing file?(y/n): ") == "y" else False

    if new_f:
        file_name = filedialog.askopenfilename()
    else:
        group_name = input("What is the group name?: ")
        file_name = f"{group_name}_phonebook.csv"

    with open(file_name, "a", newline="") as csv_file:
        field_names = list(ext_list[0].keys())
        csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
        if not new_f:
            csv_writer.writeheader()
            logger.info(f"New csv file created: {file_name}")
        csv_writer.writerows(ext_list)

    file_name = file_name.split("/")[-1]
    logger.info(f"Extension Data writen to file {file_name}.")
    return True


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    token = get_access_token(usern, passw)

    try:
        i_customer = int(input("Customer id unique: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    site_name = get_customer_name(token, i_customer)
    sd_list = get_speed_dials(token, i_customer, site_name)
    save_to_csv(sd_list)

    logger.info("Operation Complete.")
    input("Operation Complete.")


if __name__ == "__main__":
    main()
