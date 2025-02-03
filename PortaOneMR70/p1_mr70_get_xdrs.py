import json
import os
import sys

import requests

from dotenv import load_dotenv

HOSTNAME = ''
USER = 'JOROUX'

load_dotenv("env/.env")
PASSWORD = os.environ['PASSWORD']
TOKEN = os.environ['TOKEN']


def url_builder(api_url: str, session_id: str, params: str) -> str:
    full_url = HOSTNAME + api_url + '/' + session_id + '/' + params
    return full_url


def main():
    full_url = url_builder('Session/login', '', '{"login":"' + USER + '","token":"' + TOKEN + '"}')
    print(full_url)
    response = requests.post(full_url, verify=False)
    print(response.json())

    api_url = 'Customer/get_customer_list'
    session_id = '{"session_id":"' + response.json()['session_id'] + '"}'
    params = '{"limit":"50","offset":"0"}'
    full_url = url_builder(api_url, session_id, params)
    print(full_url)
    response = requests.post(full_url, verify=False)
    print(response.json())

    customer_list = response.json()['customer_list']

    i_customer_list = [x["i_customer"] for x in customer_list]
    print(i_customer_list)

    report_list = []
    api_url = 'Customer/get_custom_xdr_report_list'
    for x in i_customer_list:
        params = '{"i_customer":"' + str(x) + '"}'
        full_url = url_builder(api_url, session_id, params)
        response = requests.post(full_url, verify=False)
        print(response.json())
        response = response.json()['report_list']
        customer_reports = [a['file_name'] for a in response]
        report_list.extend(customer_reports)

    print(report_list)

    api_url = 'Customer/get_custom_xdr_report'
    for x in i_customer_list:
        for a in report_list:
            a: str
            if a.find(str(x)) > -1:
                params = '{"i_customer":"' + str(x) + '","file_name":"' + a + '"}'
                full_url = url_builder(api_url, session_id, params)
                response = requests.post(full_url, verify=False)
                with open('reports/' + a, 'wb') as report:
                    report.write(response.content)

    sys.exit(0)


if __name__ == "__main__":
    main()
