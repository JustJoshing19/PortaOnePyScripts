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
USERNAME = os.getenv("USER")
URL = os.getenv("URL")

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


def get_access_token(username: str, api_token: str) -> str:
    """Get session ID to use for API calls.

    Parameters
    ----------
        username : str
            PortaOne username used to access Porta Billing.
        api_token : str
            PortaOne user's API token used to request access.

    Returns
    -------
        str
            Session ID used for making API calls.
    """
    login_api_url = URL + "Session/login"
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

    access_token = response.json()['access_token']

    return access_token


def get_customer_invoices(access_token: str, i_customer: int) -> list[dict]:
    """

    :param access_token:
    :param i_customer:
    :return:
    """
    invoices: list[dict] = []

    inv_url = URL + "Invoice/get_invoice_list"
    inv_header = {"Authorization": f"Bearer {access_token}"}
    inv_body = {
        "params": {
            "i_customer": i_customer
        }
    }

    response = requests.post(url=inv_url, headers=inv_header, json=inv_body, verify=False)

    if response.status_code == 500:
        logger.error("An Error occurred: " + str(response.json()))
        sys.exit(1)

    invoices = response.json()["invoice_list"]

    return invoices


def prep_payment_data(inv_list: list[dict], i_customer: int) -> list[dict]:
    """

    :param i_customer:
    :param inv_list:
    :return:
    """
    inv_data: list[dict] = []

    for data in inv_list:
        inv = {
            "action": "Manual Payment",
            "amount": data["amount_due"],
            "i_customer": i_customer,
            "visible_comment": f"{data['issue_date']} invoice payment"
        }
        inv_data.append(inv)

    return inv_data


def pay_customer_invoices(access_token: str, inv_list: list[dict]) -> bool:
    """

    :param access_token:
    :param inv_list:
    :return:
    """
    pay_url = URL + "Customer/make_transaction"
    pay_header = {"Authorization": f"Bearer {access_token}"}

    for data in inv_list:
        pay_body = data

        response = requests.post(url=pay_url, headers=pay_header, json=pay_body, verify=False)

        if response.status_code == 500:
            logger.error(f"An error occurred: {response.json()}")
            return False

    return True


def main():
    token = get_access_token(USERNAME, TOKEN)
    try:
        i_customer = int(input("Please Enter the customers unique id: "))
    except ValueError as e:
        logger.error("An Error occurred: " + str(e))
        sys.exit(1)

    inv_list = get_customer_invoices(token, i_customer)
    print(inv_list)
    inv_list = prep_payment_data(inv_list, i_customer)
    print(inv_list)

    sys.exit(0)


if __name__ == "__main__":
    main()
