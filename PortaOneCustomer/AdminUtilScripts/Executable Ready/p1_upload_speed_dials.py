import csv
import json.decoder
import logging
import sys
from datetime import datetime
from getpass import getpass
from time import process_time
from tkinter import filedialog

import requests

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = "Upload_Abbreviated_numbers_" + str(log_time)
logging.basicConfig(filename=logging_name + '.log',
                    filemode='a',
                    format='%(asctime)s, %(msecs)-3d ms || %(name)-22s ' +
                           '%(levelname)-5s ' +
                           '|| %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger("Full Import Logger")


# endregion

def add_abbr_number(session_id: str, i_customer: int, **kwargs) -> True:
    """Upload abbreviated numbers data customer.

    Parameters
    ----------
        session_id : str
            Session id used to make API calls.

        i_customer : int
            The id of the customer where abbreviated numbers will be uploaded to.

        kwargs : dict
            Abbreviated number data.

    Returns
    -------
        bool
            Returns True if abbreviated number was successfully uploaded to customer, else False.
    """
    add_abbr_number_url = "/Customer/add_abbreviated_dialing_number"
    add_abbr_number_header = {"Authorization": f"Bearer {session_id}"}
    add_abbr_number_body = {
        "params": {
            "abbreviated_dialing_number_info": kwargs,
            "i_customer": i_customer
        }
    }

    t1_start = process_time()
    response = requests.post(add_abbr_number_url, headers=add_abbr_number_header, json=add_abbr_number_body,
                             verify=False)
    t1_stop = process_time()
    turnaround_time = round((t1_stop - t1_start) * 1000)

    print(f"Turn around time: {turnaround_time}")
    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        sys.exit(1)

    try:
        response.json()
    except json.decoder.JSONDecodeError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log. Please make sure you are not on a VPN.")
        sys.exit(1)

    logger.info("Abbreviated Number Uploaded.")
    return True


def upload_customer_abbr_numbers(session_id: str, abbr_list: list[dict], i_customer: int) -> bool:
    """Upload abbreviated numbers data customer.

    Parameters
    ----------
        session_id : str
            Session id used to make API calls.

        abbr_list : list[dict]
            List of abbreviated number data, stored separately in dictionaries.

        i_customer : int
            The id of the customer where abbreviated numbers will be uploaded to.

    Returns
    -------
        bool
            Returns True if all abbreviated numbers were successfully upload to customer, else False.
    """
    for row in abbr_list:
        add_abbr_number(session_id, i_customer,
                        abbreviated_number=row['abbrNum'],
                        description=row['description'],
                        number_to_dial=row['numberToDial'])

    logger.info("All Abbreviated Numbers Uploaded.")
    return True


def get_abbr_numbers_data(file_path: str) -> list[dict]:
    """Get abbreviated number data from csv file.

    Parameters
    ----------
        file_path : str
            File path of the csv file that the abbreviated number data is stored on.

    Returns
    -------
        list[dict]
            Returns a list of abbreviated number data, stored separately in dictionaries.
    """
    abbr_list: list[dict] = []

    with open(file_path, 'r') as csv_file:
        dict_reader = csv.DictReader(csv_file)
        for row in dict_reader:
            row: dict
            abbr_list.append(row)

    if not abbr_list:
        logger.error("CSV is empty")
        input("CSV is empty")
        sys.exit(1)

    if not {"abbrNum", "description", "numberToDial"}.issubset(list(abbr_list[0].keys())):
        logger.info("CSV does not contain all columns required: abbrNum, description, numberToDial")
        input("Could not find all required columns.\n"
              "Please be sure that your CSV file has ONLY the following columns:\n"
              "abbrNum\n"
              "description\n"
              "numberToDial\n\n"
              "These are case sensitive.")
        sys.exit(1)

    return abbr_list


def get_session_id(username: str, passw: str) -> str:
    """Get session ID to use for API calls.

    Parameters
    ----------
        username : str
            PortaOne username used to access Porta Billing.
        passw : str
            PortaOne user's password used to request access.

    Returns
    -------
        str
            Session ID used for making API calls.
    """
    login_api_url = "/Session/login"
    login_body = {
        'params': {
            'login': username,
            'password': passw
        }}

    t1_start = process_time()
    response = requests.post(login_api_url, json=login_body, verify=False)
    t1_stop = process_time()

    turnaround_time = round((t1_stop - t1_start) * 1000)
    print(turnaround_time)
    if response.status_code == 500:
        logger.error("An Error Occurred: ")
        sys.exit(1)

    try:
        response.json()
    except json.decoder.JSONDecodeError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log. Please make sure you are not on a VPN.")
        sys.exit(1)

    session_id = response.json()['access_token']

    logger.info("Access token retrieved successfully.")
    return session_id


def main():
    print("-------------------------------------------------------------------------------------------")
    print("This program will upload speed dials (abbreviated numbers) from a given csv file to a customers site.")
    print("CSV files used need these columns: abbrNum (Where the short number will be.), description (A short \n"
          "description, like a name), numberToDial (The full number in E. 164 format.)")
    print("-------------------------------------------------------------------------------------------")
    print()
    file_path = filedialog.askopenfilename()

    user = input("Please provide username: ")
    passw = getpass("Please provide password: ")

    session_id = get_session_id(user, passw)

    try:
        i_customer = int(input("i_customer?: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    abbr_list = get_abbr_numbers_data(file_path)
    upload_customer_abbr_numbers(session_id, abbr_list, i_customer)

    input("Upload Complete.")
    sys.exit(0)


if __name__ == "__main__":
    main()
