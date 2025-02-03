import json
import logging
import re
import sys
from datetime import datetime
from getpass import getpass

import requests
import csv
import uuid

from time import process_time
from tkinter import filedialog

PINCODE_PROD_CODE = 29158
URL = ""

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = "Import_Pincodes_" + str(log_time)
logging.basicConfig(filename=logging_name + '.log',
                    filemode='a',
                    format='%(asctime)s, %(msecs)-3d ms || %(name)-22s ' +
                           '%(levelname)-5s ' +
                           '|| %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.NOTSET)
logger = logging.getLogger("Full Import Logger")

# endregion


print("-------------------------------------------------------------------------------------------")
print("This program will add pincodes from a given customers site.")
print("-------------------------------------------------------------------------------------------")
print()
user = input("Please provide username: ")
password = getpass("Please provide password: ")

try:
    i_customer = int(input("i_customer?: "))
except ValueError as e:
    logger.error("An Error Occurred: " + str(e))
    input("An Error Occurred. Check Log.")
    sys.exit(1)

confirmation = input(f"Is {i_customer} the correct site/customer ID (y/n): ")
if confirmation != "y":
    logger.info(f"Input given {confirmation}")
    logger.info("Pincodes Import cancelled.")
    input("Canceled Operation.")
    sys.exit(1)

# region Authenticate User and get session credentials to call other PortaOne API methods
try:
    login_api_url = URL + "Session/login"
    login_body = {'params': {'login': user, 'password': password}}

    t1_start = process_time()
    response = requests.post(login_api_url, json=login_body, verify=False)
    t1_stop = process_time()
    turnaround_time = round((t1_stop - t1_start) * 1000)

    print(turnaround_time)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        print("An Error Occurred")
        sys.exit(1)

    logger.info("Access Token Retrieved Successfully.")

    access_token = response.json()['access_token']  # Store access token for future API calls
    expires_at = response.json()['expires_at']  # Store access token expiry date for if refresh is needed

    print(expires_at)
    # endregion

    # region Read pincode csv
    file_path = filedialog.askopenfilename()
    pincodeList: list[list[str]] = []
    try:
        with open(file_path, 'r') as pincodeCSV:
            csv_reader = csv.DictReader(pincodeCSV)
            for row in csv_reader:
                row: dict
                pincodeList.append([row['pincode'], row['firstName'], row['lastName']])

        for row in pincodeList:
            if (row[1] == "") | (row[2] == ""):
                logger.error(
                    "A firstName/lastName entry in the CSV file is empty, please make sure all names are not empty.")
                input("A firstName/lastName entry in the CSV file is empty, please make sure all names are not empty.")
                sys.exit(1)

            if not re.search(r"^\d{1,6}$", row[0]):
                raise ValueError

    except KeyError as e:
        logger.error("Could not find " + str(e) + " column.")
        input("Could not find " + str(e) + " column.\n"
                                           "Please be sure that your pincode CSV file have ONLY the following "
                                           "columns:\n"
                                           "pincode\n"
                                           "firstName\n"
                                           "lastName\n\n"
                                           "These are case sensitive.")
        sys.exit(1)

    except ValueError as e:
        logger.error("Pincode is not a number.")
        input("Pincode is not a number. Please make sure the pincodes are all numbers and are six digits long.")
        sys.exit(1)

    logger.info("Pincodes retrieved from csv file.")
    print(pincodeList)
    # endregion

    # region get all accounts of customer
    # Make call to API to retrieve a list of accounts that belong to the given customer ID (i_customer)
    phAccountList: list[list[str | int]] = []
    list_accounts_url = URL + "Account/get_account_list"
    list_accounts_header = {"Authorization": f"Bearer {access_token}"}

    limit = 200
    offset = 0

    while True:
        list_accounts_body = {
            "params": {
                "bill_status": "O",
                "i_customer": i_customer,
                "id": "ph%",
                "billing_model": 1,
                "limit": limit,
                "offset": offset
            }
        }
        t1_start = process_time()
        response = requests.post(list_accounts_url, headers=list_accounts_header, json=list_accounts_body, verify=False)
        t1_stop = process_time()
        turnaround_time = round((t1_stop - t1_start) * 1000)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            print("An Error Occurred")
            sys.exit(1)

        if not response.json()['account_list']:
            break

        offset += limit

        for ph_account in response.json()['account_list']:
            if ph_account["i_product"] != PINCODE_PROD_CODE:
                ph_id = ph_account["id"]
                i_account = ph_account["i_account"]
                phAccountList.append([ph_id, i_account])
    # endregion

    logger.info(f"Accounts retrieved from customer {i_customer}")
    duplicate_list: list[dict] = []
    # region Add pincode account into customer
    for pinAccount in pincodeList:
        firstName = pinAccount[1]
        lastName = pinAccount[2]
        pincodeID = "PIN_" + pinAccount[0] + "_" + firstName + "." + lastName

        if len(pincodeID) >= 64:
            pincodeID = input(f"'{pincodeID}' is too long, please enter shorter name: ")

        sip_account_password = uuid.uuid4()
        sip_account_password = str(sip_account_password)[:15]

        add_sip_account_api_url = URL + "Account/add_account"
        add_sip_account_headers = {"Authorization": f"Bearer {access_token}"}
        add_sip_account_body = {
            "params": {
                "account_info": {
                    "billing_model": 1,
                    "h323_password": sip_account_password,
                    "i_customer": i_customer,
                    "i_product": PINCODE_PROD_CODE,
                    "id": pincodeID,
                    "firstname": firstName,  # Firstname from CSV
                    "lastname": lastName  # Lastname from CSV
                }
            }
        }

        print(f'Add Account Body: {add_sip_account_body}')

        t1_start = process_time()
        sip_account_response = requests.post(add_sip_account_api_url, json=add_sip_account_body,
                                             headers=add_sip_account_headers, verify=False)
        t1_stop = process_time()
        turnaround_time = round((t1_stop - t1_start) * 1000)

        if sip_account_response.status_code != 200:
            if sip_account_response.json()["faultcode"] == "Server.Account.duplicate_id":
                print("Duplicate Pincode Found")
                duplicate_list.append({
                    "pin": pinAccount[0],
                    "first": pinAccount[1],
                    "last": pinAccount[2]
                })
                continue
            logger.error("An Error Occurred: " + str(sip_account_response.json()))
            input("An Error Occurred")
            sys.exit(1)

        print(
            f'Create pin code: response_code={sip_account_response.status_code}, turnaround_time:'
            f' {turnaround_time}ms')

        i_pincode_account = sip_account_response.json()['i_account']
        logger.info(f"Pincode created successfully: {i_pincode_account}")

        # region Add ph accounts to pincode account as aliases
        for phAccount in phAccountList:
            alias_id = f"{phAccount[0]}#{pinAccount[0]}"

            if len(alias_id) >= 64:
                alias_id = input(f"'{alias_id}' is too long, please enter shorter name: ")

            add_alias_url = URL + "Account/add_alias"
            add_alias_header = {"Authorization": f"Bearer {access_token}"}
            add_alias_body = {
                "params": {
                    "alias_info": {
                        "i_master_account": i_pincode_account,
                        "i_account": int(phAccount[1]),
                        "id": alias_id
                    }
                }
            }

            t1_start = process_time()
            response = requests.post(add_alias_url, headers=add_alias_header,
                                     json=add_alias_body, verify=False)
            t1_stop = process_time()
            turnaround_time = round((t1_stop - t1_start) * 1000)

            print(turnaround_time)

            if response.status_code == 500:
                logger.error("An Error Occurred: " + str(response.json()))
                print("An Error Occurred")
                sys.exit(1)

            logger.info(f"Pincode Alias {alias_id} created for pincode account {i_pincode_account}")
        # endregion
    # endregion
    if duplicate_list:
        with open("Duplicate_Pins.csv", "a", newline="") as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=["pin", "first", "last"])
            csv_writer.writeheader()
            csv_writer.writerows(duplicate_list)

except json.decoder.JSONDecodeError as e:
    logger.error("An Error Occurred: " + str(e))
    input("An Error Occurred. Please make sure you are not on a vpn.")
    sys.exit(1)

logger.info("Operation Complete")
input("Done adding pin codes.")
sys.exit(0)
