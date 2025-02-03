import base64
import csv
import http.client
import json
import json.decoder
import logging
import os
import sys
from datetime import datetime
from getpass import getpass
from tkinter import filedialog

from dotenv import load_dotenv

URL = ""

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = "Upload_PBK_" + str(log_time)
logging.basicConfig(filename=logging_name + '.log',
                    filemode='a',
                    format='%(asctime)s, %(msecs)-3d ms || %(name)-22s ' +
                           '%(levelname)-5s ' +
                           '|| %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.NOTSET)
logger = logging.getLogger("Full Import Logger")

# endregion


load_dotenv("env/.env")

TOKEN = os.getenv("ECN_TOKEN")
USERNAME = os.getenv("ECN_USERNAME")


def get_access_token(usern: str, passw: str) -> str:
    """Get session ID to use for API calls.

    Returns
    -------
        str
            Session ID used for making API calls.
    """
    pre_encoded_string = f"{usern}:{passw}"
    b64_encoded_string = base64.b64encode(pre_encoded_string.encode("ascii"))
    access_token = b64_encoded_string.decode("ascii")

    return access_token


def get_pbk_data() -> list[dict]:
    phonebook_num_list: list[dict] = []
    with open(filedialog.askopenfilename(), "r") as file:
        csv_file = csv.DictReader(file)
        for number in csv_file:
            number: dict
            pbk_entry = {
                "ct_displayName": number["display_name"],
                "ct_officeNumber": number["office_number"],
                "ct_mobileNumber": None,
                "ct_line": "0",
                "ct_groupName": "All Contacts"
            }
            phonebook_num_list.append(pbk_entry)

    return phonebook_num_list


def upload_pbk(i_customer: int, pbk_file_name: str, pbk_number_list: list[dict]) -> bool:
    basic_auth = f"{USERNAME}:{TOKEN}".encode("ascii")
    basic_auth = base64.b64encode(basic_auth)
    basic_auth = basic_auth.decode("ascii")

    conn = http.client.HTTPSConnection("")
    payload = json.dumps({
        "pbk_groups": [
            {
                "gp_displayName": "All Contacts"
            },
            {
                "gp_displayName": "Blacklist"
            }
        ],
        "pbk_contacts": pbk_number_list,
        "instance": "Gijima",
        "i_customer": i_customer,
        "pbk_filename": pbk_file_name
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {basic_auth}'
    }
    conn.request("POST", "//ws/simple/createPhonebook", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))

    return True


def main():
    try:
        i_customer = int(input("Unique customer ID: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    pbk_file_name = input(
        "Please provide a filename for this phonebook (Names already uploaded will overwrite phonebooks):\n")

    pbk_numbers_list = get_pbk_data()

    upload_pbk(i_customer, pbk_file_name, pbk_numbers_list)

    logger.info("Phonebook uploaded.")


if __name__ == "__main__":
    main()
