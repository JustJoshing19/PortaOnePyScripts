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

def main():
    file_l = filedialog.askopenfilename()
    raw_data: list[dict] = []
    with open(file_l, 'r') as csv_file:
        csv_writer = csv.DictReader(csv_file)
        for row in csv_writer:
            row: dict
            raw_data.append(row)

    print(raw_data)

    formatted_data: list[dict] = []
    for row in raw_data:
        phName = "ph" + row["i_customer"] + "x" + row["extension"]
        phAccount = 0
        mac = row["accessDeviceEndpoint.accessDevice.macAddress"]
        firstName = row["firstName"]
        lastName = row["lastName"]
        row = {"phName": phName, "phAccount": phAccount, "accessDeviceEndpoint.accessDevice.macAddress": mac,
               "firstName": firstName, "lastName": lastName}
        formatted_data.append(row)

    print(formatted_data)

    file_name = file_l.split("/")[-1]

    with open("fixed_file" + file_name, "a", newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, ["phName", "phAccount",
                                               "accessDeviceEndpoint.accessDevice.macAddress",
                                               "firstName", "lastName"])
        csv_writer.writeheader()
        csv_writer.writerows(formatted_data)


if __name__ == "__main__":
    main()
