import csv
import logging
import smtplib
import sys
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from getpass import getpass
from time import process_time
from tkinter import filedialog

import requests

URL = ""

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = "Trunk_DID_Mover_" + str(log_time)
logging.basicConfig(filename=logging_name + '.log',
                    filemode='a',
                    format='%(asctime)s, %(msecs)-3d ms || %(name)-22s ' +
                           '%(levelname)-5s ' +
                           '|| %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.NOTSET)
logger = logging.getLogger("Full Import Logger")


# endregion


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
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    logger.info("Token retrieved.")
    access_token = response.json()['access_token']

    return access_token


def get_account_i_dids(access_token: str, i_account: int) -> list[dict]:
    """

    :param access_token:
    :param i_account:
    :return:
    """
    limit = 200
    offset = 0

    i_did_list: list[dict] = []
    i_did_url = URL + "Account/get_alias_list"
    i_did_header = {"Authorization": f"Bearer {access_token}"}
    while True:
        i_did_body = {
            "params": {
                "i_master_account": i_account,
                "limit": limit,
                "offset": offset
            }
        }

        response = requests.post(url=i_did_url, headers=i_did_header, json=i_did_body, verify=False)

        if response.status_code == 500:
            logger.error("An error Occurred: " + str(response.json()))
            sys.exit(1)

        if not response.json()["alias_list"]:
            break

        for i_did in response.json()["alias_list"]:
            i_did_list.append({"i_account": i_did["i_account"], "id": i_did["id"]})

        offset += limit

    logger.info(f"Retrieved aliases from account {i_account}")
    return i_did_list


def delete_aliases(access_token: str, i_account: int, i_did_list: list[dict]) -> bool:
    """

    :param i_account:
    :param access_token:
    :param i_did_list:
    :return:
    """
    release_did_url = URL + "Account/delete_alias"
    release_did_header = {"Authorization": f"Bearer {access_token}"}

    for data in i_did_list:
        release_did_body = {
            "params": {
                "alias_info": {
                    "i_account": data["i_account"],
                    "i_master_account": i_account
                },
                "release_assigned_did": 0
            }
        }

        response = requests.post(url=release_did_url, headers=release_did_header, json=release_did_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            sys.exit(1)

    return True


def add_aliases_to_account(access_token: str, i_account, i_did_list: list[dict]) -> bool:
    """

    :param access_token:
    :param i_account:
    :param i_did_list:
    :return:
    """
    alias_url = URL + "Account/add_alias"
    alias_header = {"Authorization": f"Bearer {access_token}"}

    for data in i_did_list:
        alias_body = {
            "params": {
                "alias_info": {
                    "i_account": data["i_account"],
                    "id": data["id"],
                    "i_master_account": i_account
                }
            }
        }

        response = requests.post(url=alias_url, headers=alias_header, json=alias_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            sys.exit(1)

    return True


def create_move_csv(i_did_list: list[dict], i_account: int, i_master_account: int) -> bool:
    """

    :param i_did_list:
    :param i_account:
    :param i_master_account:
    :return:
    """
    if not i_did_list:
        logger.error("No DIDs to move.")
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    csv_name = f"DID_list_{i_account}_to_{i_master_account}_" + str(datetime.now().date()) + ".csv"
    with open(csv_name, "a", newline="") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=list(i_did_list[0].keys()))
        csv_writer.writeheader()
        for data in i_did_list:
            csv_writer.writerow(data)

    return True


def get_file_did_list(acc_did_list: list[dict]) -> list[dict]:
    """Gets a list of DIDs from a CSV file that will be moved between accounts.

    :param acc_did_list: DIDs that are the aliases for the origin account.

    :return: DIDs that match those that are aliases under the origin account.
    """
    match_list: list[dict] = []
    file_did_list: list[dict] = []
    file_path = filedialog.askopenfilename(filetypes=(("CSV Files", "*.csv"),))
    try:
        with open(file_path, "r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for data in csv_reader:
                data: dict
                file_did_list.append(data)
    except FileNotFoundError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    for did in file_did_list:
        try:
            id_matches = [data for data in acc_did_list if did["id"] == data["id"]]
        except KeyError as e:
            logger.error("An Error Occurred: " + str(e) + " is not a column in the selected CSV file.")
            input("An Error Occurred. Check Log.")
            sys.exit(1)
        if not id_matches:
            logger.info(f"DID with id {did['id']} was not found on the origin trunk.")
            print(f"DID with id {did['id']} was not found on the origin trunk.")
            continue
        match_list.append(id_matches[0])

    return match_list


def send_log(log_file_name: str, **user_info) -> bool:
    """

    :param log_file_name:
    :return:
    """
    port = 465
    host = "smtp.gmail.com"
    sender_email = "remote.play.fat1ma@gmail.com"
    passw = "mjzh vlkx xupm jndi"  # getpass("Password: ")
    receiver_email = "remote.play.fat1ma@gmail.com"

    date_time = str(datetime.strftime(datetime.now(), '%d-%m-%Y %H-%M-%S'))

    message = MIMEMultipart("alternative")
    message["Subject"] = "Fail Over Log " + date_time
    message["From"] = sender_email
    message["To"] = receiver_email

    email_text = build_log_email(user=user_info["usern"],
                                 origin=user_info["origin"], origin_name=user_info["origin_name"],
                                 destination=user_info["destination"],
                                 num_dids=user_info["num_dids"], cust_name=user_info["cust_name"],
                                 date_time=date_time, user_email=user_info["user_email"])
    email_text = MIMEText(email_text, "html")
    message.attach(email_text)

    try:
        with open(log_file_name, "rb") as log_file:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(log_file.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                "attachment", filename=log_file_name.split("/")[-1]
            )
            message.attach(part)
    except FileNotFoundError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    with smtplib.SMTP_SSL(host, port) as server:
        server.login(sender_email, passw)
        server.sendmail(sender_email, receiver_email, message.as_string())

    logger.info(f"Email sent to {receiver_email}.")
    return True


def build_log_email(**user_info) -> str:
    """Builds the email text that will be sent with the log file.

    :param user_info: Information with regard to the movement of DIDs between accounts.
    :return: Built email text.
    """
    o_name = user_info["origin_name"]
    d_name = ""
    match o_name:
        case "Teams":
            d_name = "Yaxxa"
        case "Yaxxa":
            d_name = "Teams"

    text = f"""
    <html>
    <body>
    <header>
        <h1>
            Fail Over Log
        </h1>
    </header>
    <p>
    Movement Information<br><br>

    Number of DIDs: {user_info["num_dids"]}<br>
    Completion Time: {user_info["date_time"]}<br>
    Origin: {o_name}<br>
    Origin account id: {user_info["origin"]}<br>
    Destination: {d_name}<br>
    Destination account id: {user_info["destination"]}<br>
    User: {user_info["user"]}<br>
    User's email: {user_info["user_email"]}<br>
    </p>
    <p>
        Please find attached the log file generated by the script.
    </p>
    </body>
    </html>
    """
    return text


def get_customer_name(token: str, i_account: int) -> list[str]:
    """

    :param token:
    :param i_account:
    :return:
    """

    url = URL + "Account/get_account_info"
    header = {"Authorization": f"Bearer {token}"}
    body = {
        "params": {
            "i_account": i_account
        }
    }

    response = requests.post(url=url, headers=header, json=body, verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    return [response.json()["account_info"]["customer_name"], response.json()["account_info"]["firstname"]]


def get_user_email(token: str, username: str) -> str:
    """

    :param token:
    :param username:
    :return:
    """
    url = URL + "User/get_user_list"
    header = {"Authorization": f"Bearer {token}"}
    body = {
        "params": {
            "login": username
        }
    }

    response = requests.post(url=url, headers=header, json=body, verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    return response.json()["user_list"][0]["email"]


def main():
    usern = input("Username: ")
    passw = getpass("Password: ")

    token = get_access_token(usern, passw)
    try:
        origin_i_account = int(input("Please enter the unique account id where the DID's are located: "))
        destination_i_account = int(input("Please enter the unique account id that the DID's need got to: "))

        file_dids = input("Is there a file with the DID info list? (Y/N): ")
        match file_dids.lower():
            case "y":
                need_file = True
            case "n":
                need_file = False
            case _:
                logger.error("Incorrect input was given.")
                input("Incorrect input was given.")
                sys.exit(1)

    except ValueError as e:
        logger.error("An Error Occurred: " + str(e))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    user_email = get_user_email(token, usern)
    cust_acc_name = get_customer_name(token, origin_i_account)
    i_did_list = get_account_i_dids(token, origin_i_account)
    if need_file:
        i_did_list = get_file_did_list(i_did_list)

    create_move_csv(i_did_list, origin_i_account, destination_i_account)
    delete_aliases(token, destination_i_account, i_did_list)
    add_aliases_to_account(token, destination_i_account, i_did_list)

    logger.info("Operation Complete.")

    send_log(logging_name + ".log", usern=usern,
             origin=origin_i_account, origin_name=cust_acc_name[1],
             destination=destination_i_account, num_dids=len(i_did_list),
             cust_name=cust_acc_name[0], user_email=user_email)

    input("Operation Complete.")
    sys.exit(0)


if __name__ == "__main__":
    main()
