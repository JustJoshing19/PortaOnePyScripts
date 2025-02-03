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
from tkinter import filedialog, Tk, Button
from tkcalendar import Calendar

URL = ""

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = "Rerate_XDR_" + str(log_time)
logging.basicConfig(filename=logging_name + '.log',
                    filemode='a',
                    format='%(asctime)s, %(msecs)-3d ms || %(name)-22s ' +
                           '%(levelname)-5s ' +
                           '|| %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger("Full Import Logger")

# endregion

root: Tk


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

    return access_token


def rerate_customer_xdrs(token: str, i_customer: int, correct_tariff: int, wrong_tariff: int,
                         from_to_date: list[str]) -> bool:
    """

    :param correct_tariff:
    :param from_to_date:
    :param i_customer:
    :param token:
    :param wrong_tariff:
    :return:
    """

    rerate_url = URL + "Tariff/rerate_xdrs"
    rerate_header = {"Authorization": f"Bearer {token}"}
    rerate_body = {
        "params": {
            "date_from": from_to_date[0],
            "date_to": from_to_date[1],
            "i_owner": i_customer,
            "i_service": 3,
            "i_tariff_correct": correct_tariff,
            "i_tariff_wrong": wrong_tariff,
            "owner": "customer"
        }
    }

    response = requests.post(url=rerate_url, headers=rerate_header, json=rerate_body, verify=False,)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        print("An Error Occurred")
        sys.exit(1)

    logger.info(f"{response.json()['xdrs_rerated']} XDRs Updated for customer {i_customer}.")
    return True


def get_date_range() -> list[str]:
    """

    :return:
    """
    global root
    from_to_date: list[str] = []
    root = Tk()
    root.title("Start Date")
    root.geometry("400x300")
    cal = Calendar(root, selectmode="day")
    cal.pack(pady=20)
    Button(root, text="Select Date", command=close_selector).pack(pady=20)
    root.mainloop()

    date_split = cal.get_date().split('/')
    from_to_date.append(f"20{date_split[2]}-{date_split[0].zfill(2)}-{date_split[1].zfill(2)} 00:00:00")

    root = Tk()
    root.title("End Date")
    root.geometry("400x300")
    cal = Calendar(root, selectmode="day")
    cal.pack(pady=20)
    Button(root, text="Select Date", command=close_selector).pack(pady=20)
    root.mainloop()

    date_split = cal.get_date().split('/')
    from_to_date.append(f"20{date_split[2]}-{date_split[0].zfill(2)}-{date_split[1].zfill(2)} 23:59:59")

    return from_to_date


def close_selector() -> bool:
    """

    :return:
    """
    root.destroy()
    return True


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    token = get_access_token(usern, passw)

    try:
        i_customer = int(input("Please provide unique id of the customer: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    from_to_date = get_date_range()

    i_tariff_incorrect = int(input("Provide the unique id of the incorrect tariff: "))
    i_tariff_correct = int(input("Provide the unique id of the correct tariff: "))

    rerated_xdrs = rerate_customer_xdrs(token, i_customer, i_tariff_correct, i_tariff_incorrect, from_to_date)
    input("Rerating Done!")
    sys.exit(0)


if __name__ == "__main__":
    main()
