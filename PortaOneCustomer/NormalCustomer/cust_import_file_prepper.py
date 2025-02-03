import csv
import logging
import os
from datetime import datetime
from tkinter import filedialog

from dotenv import load_dotenv

load_dotenv("SingleTaskScripts/env/.env")

TOKEN = os.getenv("API_TOKEN")
USERNAME = "joshuar"

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = ""
logging.basicConfig(filename=logging_name + '.log',
                    filemode='a',
                    format='%(asctime)s, %(msecs)-3d ms || %(name)-22s ' +
                           '%(levelname)-5s ' +
                           '|| %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger("Full Import Logger")


# endregion


def get_csv_data(file_location: str) -> list[dict]:
    """Retrieve data from csv for it to be prepped

    :param file_location: CSV location.
    :return: Data retrieved from csv file.
    """
    data: list[dict] = []
    with open(file_location, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            row: dict
            data.append(row)

    return data


def fix_extensions(data: list[dict]) -> list[dict]:
    """

    :param data:
    :return:
    """
    for row in data:
        if row['extension']:
            row['extension'] = add_leading_zero(int(row['extension']))
    return data


def add_leading_zero(number: int) -> str:
    """

    :param number:
    :return:
    """
    a = "{:04d}".format(number)
    return a


def add_Missing_Columns(data: list[dict]) -> list[dict]:
    """

    :param data:
    :return:
    """
    for row in data:
        if "userLinePorts[1]" not in list(row.keys()):
            row['userLinePorts[1]'] = ""
        if "departmentName" not in list(row.keys()):
            row['departmentName'] = ""
        if "yahooId" not in list(row.keys()):
            row['yahooId'] = ""
        if "impId" not in list(row.keys()):
            row['impId'] = ""
        if "callingLineIdPhoneNumber" not in list(row.keys()):
            row['callingLineIdPhoneNumber'] = ""
        if "accessDeviceEndpoint.accessDevice.macAddress" not in list(row.keys()):
            row['accessDeviceEndpoint.accessDevice.macAddress'] = ""
    return data


def format_product(data: list[dict]) -> list[dict]:
    """

    :param data:
    :return:
    """
    products = ["connect", "cooperate", "collaborate", "communicate", "trunk"]
    for row in data:
        for prod in products:
            if prod in row["servicePacks"].lower():
                prod: str
                if prod == "trunk":
                    row["servicePacks"] = row["servicePacks"].lower()
                else:
                    row["servicePacks"] = f"UC {prod.capitalize()}"

    return data


def save_changes(file_dir: str, data: list[dict]) -> bool:
    """

    :param file_dir:
    :param data:
    :return:
    """
    with open(file_dir, 'w', newline='') as csv_file:
        keys = list(data[0].keys())
        csv_writer = csv.DictWriter(csv_file, fieldnames=keys)
        csv_writer.writeheader()
        csv_writer.writerows(data)

    return True


def main():
    file_dir = filedialog.askopenfilename()
    data = get_csv_data(file_dir)
    data = fix_extensions(data)
    data = add_Missing_Columns(data)
    data = format_product(data)
    save_changes(file_dir, data)


if __name__ == "__main__":
    main()
