import base64
import logging
import sys
import os
from datetime import datetime
from getpass import getpass
from time import process_time, sleep
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import http.client
import json
import base64

URL = ""

load_dotenv("env/.env")

TOKEN = os.getenv("ECN_TOKEN")
USERNAME = os.getenv("ECN_USERNAME")

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = "Get_Phonebook_List_" + str(log_time)
logging.basicConfig(filename=logging_name + '.log',
                    filemode='a',
                    format='%(asctime)s, %(msecs)-3d ms || %(name)-22s ' +
                           '%(levelname)-5s ' +
                           '|| %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger("Full Import Logger")


# endregion

def get_phonebook() -> list[str]:
    conn = http.client.HTTPSConnection("")
    payload = json.dumps({
        "pbk_filename": "test"
    })

    basic_auth_string = f"{USERNAME}:{TOKEN}"
    basic_auth_string = basic_auth_string.encode("ascii")
    basic_auth_string = base64.b64encode(basic_auth_string)
    basic_auth_string = basic_auth_string.decode("ascii")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': ('Basic %s' % basic_auth_string)
    }
    conn.request("POST", "//ws/simple/getPhonebook", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))


def main():
    get_phonebook()


if __name__ == "__main__":
    main()
