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
logging_name = "Add_SIP_Trunk_" + str(log_time)
logging.basicConfig(filename=logging_name + '.log',
                    filemode='a',
                    format='%(asctime)s, %(msecs)-3d ms || %(name)-22s ' +
                           '%(levelname)-5s ' +
                           '|| %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.NOTSET)
logger = logging.getLogger("Full Import Logger")

# endregion

TRUNK_PRODUCT = 34062
NUMBER_RANGES = ["2710133", "2712133", "2713133", "2714133", "2721133",
                 "2731393", "2741133", "2751133", "2787463", "2786"]

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

    access_token = response.json()['access_token']

    return access_token


def get_trunk_info() -> dict:
    """

    :return:
    """
    trunk_info = {}
    filename = filedialog.askopenfilename()

    with open(filename, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for data in csv_reader:
            data: dict
            trunk_info["firstname"] = data["firstName"]
            trunk_info["lastname"] = data["lastName"]
            trunk_info["id"] = data["phoneNumber"]

    return trunk_info


def add_trunk(token: str, trunk_data: dict) -> bool:
    """
    
    :param token: 
    :param trunk_data: 
    :return: 
    """
    try:
        i_customer = int(input("Customer id: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    sip_account_password = uuid.uuid4()
    sip_account_password = str(sip_account_password)[:15]
    add_sip_account_api_url = "/Account/add_account"
    add_sip_account_headers = {"Authorization": f"Bearer {token}"}
    add_sip_account_body = {
        "params": {
            "account_info": {
                "billing_model": 1,
                "email": "",
                "h323_password": sip_account_password,
                "i_account_role": 1,
                "i_customer": i_customer,
                "i_product": TRUNK_PRODUCT,
                "id": trunk_data["id"],
                "firstname": trunk_data["firstname"],
                "lastname": trunk_data["lastname"]
            }
        }
    }

    t1_start = process_time()
    sip_account_response = requests.post(add_sip_account_api_url, json=add_sip_account_body,
                                         headers=add_sip_account_headers, verify=False)
    t1_stop = process_time()
    turnaround_time = round((t1_stop - t1_start) * 1000)

    if sip_account_response.status_code == 500:
        logger.error("An Error Occurred: " + str(sip_account_response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    print(
        f'Create Account:  response_code={sip_account_response.status_code}, '
        f'turnaround_time: {turnaround_time}ms')
    print(sip_account_response.json())

    return True


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    token = get_access_token(usern, passw)
    trunk_data = get_trunk_info()
    add_trunk(token, trunk_data)

    input("Trunk Added")
    sys.exit(0)


if __name__ == "__main__":
    main()
