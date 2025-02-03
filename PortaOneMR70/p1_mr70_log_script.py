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


def get_logs(session_id: str, i_customer: int) -> list:
    """Retrieves logs from PortaOne about given i_customer.

    :param session_id: Required to make API calls.
    :param i_customer: Unique identifier for the customer entity.
    :return: List of logs retrieved from given customer ID.
    """
    log_list = []
    params = '{"limit": "100","entity_type":"Customers","i_entity":"' + str(i_customer) + '"}'
    full_url = url_builder('WebLog/get_web_log_list', session_id, params)

    print(full_url)
    response = requests.post(full_url, verify=False)

    log_list.extend(json_to_list(response.json()))
    log_count = response.json()["total"] - 100
    offset = 100

    while log_count > 0:
        params = '{"limit":"100","offset":"' + str(offset) + '","entity_type":"Customers","i_entity":"' + str(
            i_customer) + '"}'
        full_url = url_builder('WebLog/get_web_log_list', session_id, params)
        print(full_url)
        response = requests.post(full_url, verify=False)
        log_list.extend(json_to_list(response.json()))
        log_count -= 100
        offset += 100

    return log_list


def json_to_list(json_data: dict) -> list:
    """Extracts log list from json data provided.

    :param json_data: Dict containing a set of logs.
    :return: Logs that have been put into a list.
    """
    new_list = []
    for log in json_data['web_log_list']:
        new_list.append(log)

    return new_list


def filter_logs(logs: list) -> list:
    """Filters logs to only those that are balance adjustments

    :param logs: Unfiltered logs.
    :return: Filtered logs that only contain Balance adjustments.
    """
    balance_logs: list[list] = []
    for log in logs:
        if "" in log['description']:
            print(log['description'])
            if log['description']:
                amount = str(log['description']).split()[-1]
            else:
                amount = -1
            date_time = log['timestamp']
            user = log['username']
            balance_logs.append(["Balance Adjustment", amount, date_time, user])

    return balance_logs


def export_csv(session_id: str, log_list: list[list[str]], i_customer: int):
    """Exports log to csv file.

    :param session_id:
    :param log_list: Logs that only contain Balance adjustments.
    :param i_customer: Unique identifier for the customer entity.
    """
    params = '{"i_customer": "' + str(i_customer) + '"}'
    full_url = url_builder('Customer/get_customer_info', session_id, params)

    print(full_url)
    response = requests.post(full_url, verify=False)
    name = response.json()['customer_info']['name']

    with open("balance_adjustments_" + str(i_customer) + "_" + name + ".csv", 'a', newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Action', 'Amount', 'DateTime', 'user'])
        csv_writer.writerows(log_list)


def get_cust_list(session_id: str) -> list[int]:
    cust_list: list[int] = []
    params = '{"limit": "100","offset":"0"}'
    full_url = url_builder('Customer/get_customer_list', session_id, params)

    print(full_url)
    response = requests.post(full_url, verify=False)

    for i in response.json()['customer_list']:
        cust_list.append(i['i_customer'])

    return cust_list


def main():
    session_id = '{"session_id":"' + logon() + '"}'
    customer_list: list[int] = get_cust_list(session_id)
    for i_customer in customer_list:
        log_list = get_logs(session_id, i_customer)
        print(log_list)

        log_list = filter_logs(log_list)
        print(log_list)

        export_csv(session_id, log_list, i_customer)

    sys.exit(0)


if __name__ == "__main__":
    main()
