import csv
import logging
import os
import sys
import uuid

import requests

from datetime import datetime
from dotenv import load_dotenv
from time import process_time, sleep
from tkinter import filedialog

from requests.auth import HTTPBasicAuth

TESTING = True

load_dotenv("env/.env")

TOKEN = os.getenv("ECN_TOKEN")
USERNAME = os.getenv("ECN_USERNAME")
URL = os.getenv("ECN_URL")

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = "Auto_Prov_" + str(log_time)
logging.basicConfig(filename=logging_name + '.log',
                    filemode='a',
                    format='%(asctime)s, %(msecs)-3d ms || %(name)-22s ' +
                           '%(levelname)-5s ' +
                           '|| %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.NOTSET)
logger = logging.getLogger("Full Import Logger")


# endregion


def get_prov_data() -> list[dict]:
    """Retrieves ECN data from csv file.

    :return: ECN data that will be used for auto provisioning
    """
    ecn_file = filedialog.askopenfilename()
    prov_data: list[dict] = []

    with open(ecn_file, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:  # change name of keys for certain parameters
            row: dict
            prov_data.append(row)

    return prov_data


def prep_data(prov_data: list[dict]) -> list[dict[str, str | int]]:
    """Preps data to be used when auto provisioning API is called.

    :param prov_data: ECN data that will be used for auto provisioning
    :return: Prepared ECN data.
    """
    prepped_data: list[dict] = []
    for row in prov_data:
        acc: dict = {"i_customer": int(row["phName"][2:-5]),
                     "line_number": 1,
                     "ext_number": row["phName"][-4:],
                     "mac_address": row["accessDeviceEndpoint.accessDevice.macAddress"],
                     "display_name_first": row["firstName"],
                     "display_name_last": row["lastName"],
                     "i_model": int(row["i_model"]),
                     "porta_user": "Gijima",
                     "action": "add"}
        prepped_data.append(acc)

    return prepped_data


def send_prov_data(prov_data: list[dict]) -> bool:
    """Send data in given list to api for auto provisioning.

    :param prov_data: Data that will be sent to ECN for auto provisioning.
    :return: True if all data was successfully sent, False otherwise.
    """
    step = 20
    for x in range(0, len(prov_data), step):
        if x + step > len(prov_data):
            step = len(prov_data) % step

        ecn_body = {
            "array": prov_data[x:x + step]
        }

        print(ecn_body)
        response = requests.post(url=URL, auth=HTTPBasicAuth(username=USERNAME, password=TOKEN), json=ecn_body)
        if response.status_code != 200:
            logger.error("An Error Occurred: " + str(response.content))
            input("An Error Occurred")

        print(response.content)
        sleep(60)

    return True


def main():
    prov_data = get_prov_data()
    print(prov_data)

    prov_data = prep_data(prov_data)
    print(prov_data)

    send_prov_data(prov_data)


if __name__ == "__main__":
    main()
