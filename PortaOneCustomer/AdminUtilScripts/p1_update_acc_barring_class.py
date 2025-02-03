import csv
import logging
import os
import sys
import uuid

import requests

from datetime import datetime
from dotenv import load_dotenv
from time import process_time
from tkinter import filedialog

load_dotenv("env/.env")

TOKEN = os.getenv("API_TOKEN")
USERNAME = "joshuar"

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = "Update_Barring_" + log_time
logging.basicConfig(filename=logging_name + '.log',
                    filemode='a',
                    format='%(asctime)s, %(msecs)-3d ms || %(name)-22s ' +
                           '%(levelname)-5s ' +
                           '|| %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.NOTSET)
logger = logging.getLogger("Update Barring")


# endregion
def get_access_token(username: str, api_token: str) -> str:
    """Get access token from Porta One to make requests.

    :param username: PortaOne username used to access Porta Billing.
    :param api_token: PortaOne user's API token used to request access.

    :return: Session ID used for making API calls.
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

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    access_token = response.json()['access_token']
    logger.info("Access Token Retrieved.")

    return access_token


def get_barring_numbers(file_path: str) -> list[str]:
    """Get list containing all the numbers to be used in the call barring.

    :param file_path: Path to the csv file where data will be read from.
    :return: Number list.
    """
    barring_numbers = []
    try:
        with open(file_path, "r") as barr_file:
            csv_reader = csv.DictReader(barr_file)
            for row in csv_reader:
                row: dict
                barring_numbers.append(row["numberToDial"])
    except IndexError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    logger.info("Barring Number Retrieved")
    return barring_numbers


def update_call_barr_class(access_token: str, i_cp_condition: int, barr_numbers: list[dict[str, str]]) -> int:
    """Update Call Barring Class, adding new abbreviated numbers to the

    :param i_cp_condition: Unique id of Call Barring Class.
    :param access_token: Token required to make Porta One API.
    :param barr_numbers: List of numbers to be added to Call Barring Class.
    :return: Unique id of Call Barring Class.
    """

    update_call_barr_class_api_url = "/CallBarring/update_call_barring_class"  # Get correct api call url
    update_call_barr_class_headers = {"Authorization": f"Bearer {access_token}"}
    update_call_barr_class_body = {
        "params": {
            "call_barring_class_info": {
                "i_cp_condition": i_cp_condition,
                "number_pattern_list": barr_numbers
            }}}

    t1_start = process_time()
    update_call_barr_class_response = requests.post(update_call_barr_class_api_url,
                                                    json=update_call_barr_class_body,
                                                    headers=update_call_barr_class_headers, verify=False)
    t1_stop = process_time()
    turnaround_time = round((t1_stop - t1_start) * 1000)

    if update_call_barr_class_response.status_code == 500:
        logger.error("An Error Occurred: " + str(update_call_barr_class_response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    print(
        f'Update Call Barring Class response:  response_code={update_call_barr_class_response.status_code},'
        f'Turnaround_time: {turnaround_time}ms')

    return update_call_barr_class_response.json()["i_cp_condition"]


def main():
    access_token = get_access_token(USERNAME, TOKEN)

    file_path = filedialog.askopenfilename()

    barr_dict_list: list[dict[str, str]] = []
    barr_numbers = get_barring_numbers(file_path)
    for barr in barr_numbers:
        barr_dict_list.append({"number": barr})

    try:
        i_cp_condition = int(input("What is the unique id of number barring class?: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    i_cp_condition = update_call_barr_class(access_token, i_cp_condition, barr_dict_list)
    logger.info(f"Updated Call Barring Class: {i_cp_condition}")


if __name__ == "__main__":
    main()
