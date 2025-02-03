import csv
import os
import sys
from tkinter import filedialog

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
    full_url = url_builder('Session/login', '', '{"login":"' + USER
                           + '", "token":"' + TOKEN + '"}')
    print(full_url)
    response = requests.post(full_url, verify=False)
    check_response(response)
    return response.json()['session_id']


def make_customer_transaction(session_id: str, i_customer: int, amount: float, transaction_type: int,
                              comment: str) -> bool:
    """Adjusts the balance of given i_customer

    :param session_id: ID required to make API calls
    :param i_customer: Unique identifier of the customer
    :param amount: Amount to be adjustment
    :param transaction_type: Transaction type
    :param comment: Additional info for change
    :return: True if adjustment was successful
    """
    transaction_action: str = "Manual Charge"
    match transaction_type:
        case 2:
            transaction_action = "Manual Credit"
        case 3:
            transaction_action = "Manual Payment"
        case 4:
            transaction_action = "Promotional Credit"
        case 5:
            transaction_action = "E-Commerce Payment"
        case 6:
            transaction_action = "E-Commerce Refund"
        case 7:
            transaction_action = "Authorization Only"
        case 8:
            transaction_action = "Capture Payment"
        case 9:
            transaction_action = "Refund"

    adjust_params = ('{"action": "' + transaction_action +
                     '", "amount":' + str(amount) +
                     ', "i_customer":' + str(i_customer) +
                     ', "visible_comment":"' + comment + '"}')
    adjust_url = url_builder("Customer/make_transaction", session_id, adjust_params)
    response = requests.post(adjust_url, verify=False)

    check_response(response)

    return True


def get_adjustments(file_location: str) -> list[dict]:
    """Get adjustment amounts from given file.

    :param file_location: Location of file that contains adjustment amounts.
    :return: list of adjustments.
    """
    adjust_amounts: list[dict] = []
    with open(file_location, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            row: dict
            adjust_amounts.append(row)

    return adjust_amounts


def fix_customer_balance(session_id: str, i_customer: int, credit_charge_amounts: list[dict]) -> bool:
    """Apply charges and credits, listed in given list, to customer.

    :param session_id: ID required to make API calls
    :param i_customer: Unique identifier of the customer
    :param credit_charge_amounts: List of credits and charges that should be applied to a customer.
    :return: True if balance changes were successful.
    """
    limit_increase = 0.0
    charge_list: list[float] = []
    credit_list: list[float] = []
    invoice_list: list[str] = []
    for cc_set in credit_charge_amounts:
        limit_increase += float(cc_set["charge"])
        charge_list.append(float(cc_set["charge"]))
        credit_list.append(float(cc_set["credit"]))
        invoice_list.append(cc_set["invoice"])

    init_limit = increase_limit(session_id, i_customer, limit_increase)
    # EXCLUDING: VAT Credit Correction on xxx
    # INCLUDING: xxx Billing Upload
    for x in range(0, len(credit_charge_amounts)):
        make_customer_transaction(session_id, i_customer,
                                  charge_list[x], 1, f"Credit Correction on {invoice_list[x]}")

    for x in range(0, len(credit_charge_amounts)):
        make_customer_transaction(session_id, i_customer,
                                  credit_list[x], 3, f"{invoice_list[x]} Billing Upload")

    reset_limit(session_id, i_customer, init_limit)

    return True


def increase_limit(session_id: str, i_customer: int, limit_increase: float) -> float:
    """Increases credit limit of given customer.

    :param session_id: ID required to make API calls
    :param i_customer: Unique identifier of the customer
    :param limit_increase: The amount that the credit limit will be increased by.
    :return: The original limit that the customer had before the increase.
    """
    params = '{"i_customer":' + str(i_customer) + '}'
    full_url = url_builder("Customer/get_customer_info", session_id, params)
    response = requests.post(full_url, verify=False)
    current_limit = response.json()["customer_info"]["credit_limit"]
    new_limit = current_limit + limit_increase + 10

    params = ('{ "customer_info": {"i_customer":' + str(i_customer) +
              ', "credit_limit": ' + str(new_limit) + '}}')
    full_url = url_builder("Customer/update_customer", session_id, params)
    response = requests.post(full_url, verify=False)
    check_response(response)

    return float(current_limit)


def reset_limit(session_id: str, i_customer: int, init_limit: float) -> bool:
    """Reset credit limit of customer to its original amount.

    :param session_id: ID required to make API calls
    :param i_customer: Unique identifier of the customer
    :param init_limit: The original limit that the customer had before the increase.
    :return: True if limit was successfully set.
    """
    params = ('{"customer_info": {"i_customer": ' + str(i_customer) +
              ', "credit_limit": ' + str(init_limit) + '}}')

    full_url = url_builder("Customer/update_customer", session_id, params)
    response = requests.post(full_url, verify=False)

    check_response(response)

    return True


def check_data_format(sample: list[dict]) -> bool:
    """Checks if data values are correct and have the correct columns.

    :param sample: The data being format tested.
    :return: True if format is correct, False if not.
    """
    one_sample = sample[0]
    correct_keys = ['invoice', 'charge', 'credit']
    if not all(key in list(one_sample.keys()) for key in correct_keys):
        print(list(one_sample.keys()))
        return False

    for x in sample:
        try:
            ch = float(x['charge'])
            cr = float(x['credit'])

            if (ch < 0) or (cr < 0) or (x['invoice'] == ''):
                raise ValueError

        except ValueError:
            print(
                "\nFormat is incorrect."
                "\nA value in the 'credit' or/and 'charge' column is not a number or is a negative"
                "\nOr a cell in the 'invoice' column in empty.")
            return False

    return True


def check_response(response: requests.Response) -> bool:
    """Check whether response code is 200.

    :param response: The response received from the POST request.
    :return: True if code is 200
    """
    if response.status_code:
        return True

    print(response.json())
    print("Error occurred during API call.")
    input()
    sys.exit(1)


def main():
    # user = input("Please enter Porta username: ")
    # token = input("Please enter Porta API token: ")

    session_id = '{"session_id":"' + logon() + '"}'
    i_customer = int(input("Please enter customer's unique identifier: "))

    adjustment_file = filedialog.askopenfilename(title="Please select the adjustment file")
    if not adjustment_file:
        print("File was not selected.")
        input()
        sys.exit(0)
    elif not adjustment_file.endswith(".csv"):
        print("Wrong file type.\n"
              "Only 'csv' files are accepted.")
        input()
        sys.exit(0)

    adjust_amounts = get_adjustments(adjustment_file)
    if not adjust_amounts:
        print("File is empty")
        input()
        sys.exit(0)
    elif not check_data_format(adjust_amounts):
        print("\nData format is incorrect."
              "\nPlease have these columns and data types:"
              "\n'invoice' as text, 'charge' as numbers, 'credit' as numbers")
        input()
        sys.exit(0)

    fix_customer_balance(session_id, i_customer, adjust_amounts)

    print("Adjustment Done")
    input()
    sys.exit(0)


if __name__ == "__main__":
    main()
