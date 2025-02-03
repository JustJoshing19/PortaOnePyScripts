import csv
import logging
import sys
from datetime import datetime
from getpass import getpass
from time import process_time
from tkinter import filedialog

import requests

URL = ""

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = "Update_Phonebook_" + str(log_time)
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
        print("An Error Occurred")
        sys.exit(1)

    access_token = response.json()['access_token']

    logger.info("Access Token Received.")

    return access_token


def get_pbx_data(token: str, i_customer: int) -> list[dict]:
    """

    :param token:
    :param i_customer:
    :return:
    """
    site_name = input("Provide site name: ")

    pin_url = URL + "Account/get_account_list"
    pin_header = {"Authorization": f"Bearer {token}"}
    ext_list: list[dict] = []

    limit = 200
    offset = 0
    while True:
        ext_body = {
            "params": {
                "bill_status": "O",
                "i_customer": f"{i_customer}",
                "billing_model": 1,
                "id": "ph%",
                "limit": limit,
                "offset": offset
            }
        }  # Edit in case of more than 100 Pincodes accounts

        response = requests.post(url=pin_url, headers=pin_header, json=ext_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            sys.exit(1)

        if not response.json()["account_list"]:
            break

        offset += limit

        for ext in response.json()["account_list"]:
            ext_list.append({"display_name": ext["extension_name"],
                             "office_number": ext["extension_id"],
                             "mobile_number": "",
                             "other_number": "",
                             "line": -1,
                             "ring": "auto",
                             "auto_divert": "",
                             "priority": "",
                             "group_id_name": site_name})

    logger.info("All extensions retrieved")
    return ext_list


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
        file_name = f"{group_name.upper()}_PBK.csv"

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
        i_customer = int(input("Provide customer id: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    ext_list = get_pbx_data(token, i_customer)
    save_to_csv(ext_list)

    logger.info("Phonebook csv updated.")
    input("Phonebook csv updated.")
    sys.exit(0)


if __name__ == "__main__":
    main()
