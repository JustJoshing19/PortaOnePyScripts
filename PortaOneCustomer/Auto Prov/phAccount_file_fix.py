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

PHONE_MODELS: dict[str, int] = {"T21_E2": 101,
                                "T23": 102,
                                "T27P": 103,
                                "T29G": 104,
                                "T33G": 105,
                                "T31G": 106,
                                "T31P": 107,
                                "T40P": 108,
                                "T40G": 109,
                                "T41S": 110,
                                "T42S": 111,
                                "T43U": 112,
                                "T46U": 113,
                                "T46S": 114,
                                "T48U": 115,
                                "T48S": 116,
                                "T58A": 117,
                                "T53W": 118,
                                "T53": 119,
                                "T54W": 120,
                                "T57W": 121,
                                "W52P": 122,
                                "W53P": 123,
                                "W60B": 124,
                                "W70B": 125,
                                "W80DM": 126,
                                "W90DM": 127,
                                "CP920": 128,
                                "CP925": 129,
                                "CP930W": 130,
                                "CP960": 131,
                                "CP965": 132,
                                "T20P": 133,
                                "T21P": 134,
                                "T42G": 135,
                                "T46G": 136
                                }


def get_files() -> list[str]:
    ph_account_file = filedialog.askopenfilename(title="Please select the phAccount csv file")
    odin_file = filedialog.askopenfilename(title="Please select the oden file that matches the selected phAccount csv")
    return [ph_account_file, odin_file]


def get_data_from_file(file_locations: list[str]) -> list[list[dict]]:
    data_sets: list[list[dict]] = []
    for f_path in file_locations:
        with open(f_path, "r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            data = []
            for line in csv_reader:
                line: dict
                data.append(line)
            data_sets.append(data)

    return data_sets


def update_account_data(data_sets: list[list[dict]]) -> list[dict]:
    odin_data = data_sets[1]
    for account in data_sets[0]:
        ext = int(account["phName"][-4:])
        for line in odin_data:
            try:
                if ext == int(line["extension"]):
                    print(ext)
                    account["lastName"] = line["lastName"]
                    account["firstName"] = line["firstName"]
                    account["accessDeviceEndpoint.accessDevice.macAddress"] = line[
                        "accessDeviceEndpoint.accessDevice.macAddress"]
                    model = 0
                    for model_name in PHONE_MODELS:
                        if model_name in line["accessDeviceEndpoint.accessDevice.version"]:
                            model = PHONE_MODELS[model_name]
                            account["i_model"] = model
                    if model == 0:
                        account["i_model"] = 0
            except:
                print(line)

    return data_sets[0]


def update_file(updated_data: list[dict], file_location: str) -> bool:
    file_name = file_location.split("/")[-1]
    try:
        with open("AutoProvReady" + file_name, 'w', newline="") as csv_file:
            keys = []
            for key in updated_data[0]:
                keys.append(key)
            csv_writer = csv.DictWriter(f=csv_file, fieldnames=keys)
            csv_writer.writeheader()
            csv_writer.writerows(updated_data)
    except PermissionError as e:
        print(f"test{file_name} already exists. Please delete.")
        input()
        sys.exit(1)

    return True


def main():
    file_locations = get_files()
    print(file_locations)
    data_sets = get_data_from_file(file_locations)
    updated_data_set = update_account_data(data_sets)
    print(updated_data_set)
    update_file(updated_data_set, file_locations[0])


if __name__ == "__main__":
    main()
