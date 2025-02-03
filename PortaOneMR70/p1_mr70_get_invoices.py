import csv
import json
import os
import sys
from datetime import datetime

import requests

from dotenv import load_dotenv

HOSTNAME = ''
USER = 'JOROUX'

load_dotenv("env/.env")
PASSWORD = os.environ['PASSWORD']
TOKEN = os.environ['TOKEN']


def url_builder(api_url: str, session_id: str, params: str) -> str:
    """Builds the url that will be used to make API call to the PortaOne MR70 platform.

    :param api_url: The URL of the API call that will be made.
    :param session_id: ID of logged on session that is required to make API calls.
    :param params: Request specific, parameters required for api calls.
    :return: URL built from given parameters.
    """
    full_url = HOSTNAME + api_url + '/' + session_id + '/' + params
    return full_url


def logon() -> str:
    """Creates a login session to make sure

    :return: Session ID, used to make API calls.
    """
    full_url = url_builder('Session/login', '', '{"login":"' + USER + '","token":"' + TOKEN + '"}')
    print(full_url)
    response = requests.post(full_url, verify=False)
    print(response.json())
    return response.json()['session_id']


def get_invoices(session_id: str, i_customer: int) -> list:
    invoices = []
    params = '{"limit": "100","offset":"0","i_customer":"' + str(i_customer) + '"}'
    full_url = url_builder('Invoice/get_invoice_list', session_id, params)

    print(full_url)
    response = requests.post(full_url, verify=False)

    invoices.extend(response.json()["invoice_list"])
    log_count = response.json()["total"] - 100
    offset = 100

    while log_count > 0:
        params = '{"limit":"100","offset":"' + str(offset) + '","i_customer":"' + str(i_customer) + '"}'
        full_url = url_builder('Invoice/get_invoice_list', session_id, params)
        print(full_url)
        response = requests.post(full_url, verify=False)
        invoices.extend(response.json()["invoice_list"])
        log_count -= 100
        offset += 100

    return invoices


def main():
    session_id = '{"session_id":"' + logon() + '"}'
    print(get_invoices(session_id, 186044))
    sys.exit(0)


if __name__ == "__main__":
    main()
