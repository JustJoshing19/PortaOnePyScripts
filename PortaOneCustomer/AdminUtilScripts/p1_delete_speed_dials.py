import logging
import sys
from datetime import datetime
from getpass import getpass
from time import process_time, sleep

import requests
from dotenv import load_dotenv

load_dotenv("env/.env")

URL = ""

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = "Delete_Speed_Dials_" + str(log_time)
logging.basicConfig(filename=logging_name + '.log',
                    filemode='a',
                    format='%(asctime)s, %(msecs)-3d ms || %(name)-22s ' +
                           '%(levelname)-5s ' +
                           '|| %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger("Full Import Logger")


# endregion


def get_access_token(user: str, password: str) -> str:
    """Get session ID to use for API calls.

    Returns
    -------
        str
            Session ID used for making API calls.
    """
    login_api_url = URL + "Session/login"
    login_body = {
        'params': {
            'login': user,
            'password': password
        }}

    t1_start = process_time()
    response = requests.post(login_api_url, json=login_body, verify=False)
    t1_stop = process_time()

    turnaround_time = round((t1_stop - t1_start) * 1000)
    print(turnaround_time)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    access_token = response.json()['access_token']
    logger.info("Successfully retrieved access token.")

    return access_token


def get_speed_dials(token: str, i_customer: int) -> list[int]:
    """

    :param token:
    :param i_customer:
    :return:
    """
    limit = 200
    offset = 0
    i_ab_list = []

    get_speed_dials_url = URL + "Customer/get_abbreviated_dialing_number_list"
    get_speed_dials_headers = {"Authorization": f"Bearer {token}"}
    while True:
        get_speed_dials_body = {
            "params": {
                "i_customer": i_customer,
                "limit": limit,
                "offset": offset
            }
        }

        response = requests.post(url=get_speed_dials_url, headers=get_speed_dials_headers, json=get_speed_dials_body,
                                 verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            print("An Error Occurred")
            sys.exit(1)

        if len(response.json()["abbreviated_dialing_number_list"]) == 0:
            break

        i_ab_list.extend(response.json()["abbreviated_dialing_number_list"])
        offset += limit

    id_list = []
    for i in i_ab_list:
        id_list.append(i["i_ab_dialing"])

    logger.info(f"Abbreviated dialing numbers successfully retrieved from customer id {i_customer}")
    return id_list


def delete_speed_dials(token: str, i_ab_list: list[int]) -> bool:
    """

    :param i_ab_list:
    :param token:
    :return:
    """
    del_speed_dials_url = URL + "Customer/delete_abbreviated_dialing_number"
    del_speed_dials_header = {"Authorization": f"Bearer {token}"}
    for i_ab in i_ab_list:
        del_speed_dials_body = {
            "params": {
                "i_ab_dialing": i_ab
            }
        }

        response = requests.post(url=del_speed_dials_url, headers=del_speed_dials_header, json=del_speed_dials_body,
                                 verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            print("An Error Occurred")
            sys.exit(1)

        logger.info(f"Deleted abbreviated number {i_ab}")

    return True


def main():
    print("-------------------------------------------------------------------------------------------")
    print("This program will remove all speed dials (abbreviated numbers) from a given customers site.")
    print("-------------------------------------------------------------------------------------------")
    print()
    user = input("Please provide username: ")
    password = getpass("Please provide password: ")

    token = get_access_token(user, password)

    try:
        i_customer = int(input("Provide unique customer id: "))
    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    i_ab_list = get_speed_dials(token, i_customer)

    print(i_ab_list)

    if input("Delete speed dials? (y/n): ") != "y":
        logger.info("Speed dials deletion cancelled.")
        input("Canceling Operation.")
        sys.exit(1)

    delete_speed_dials(token, i_ab_list)
    logger.info(f"All Abbreviated Numbers Removed from customer id {i_customer}")
    input(f"All Abbreviated Numbers Removed from customer id {i_customer}")
    exit(0)


if __name__ == "__main__":
    main()
