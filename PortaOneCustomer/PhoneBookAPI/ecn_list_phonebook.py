import logging
import sys
import os
from datetime import datetime
from getpass import getpass
from time import process_time, sleep
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

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

def get_phonebook_list() -> list[str]:
    """Get a list of phonebooks from ECN.

    :return: list of phonebook names
    """
    get_phonebook_list_url = URL
    response = requests.post(url=get_phonebook_list_url, auth=HTTPBasicAuth(username=USERNAME, password=TOKEN), )

    print(response.json())
    return response.json()["pbk_filenames"]


def main():
    get_phonebook_list()


if __name__ == "__main__":
    main()
