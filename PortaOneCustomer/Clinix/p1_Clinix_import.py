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
USERNAME = "joshuar"
PROD_SUB_SETS = {"UC CONNECT": [30301, 0], "UC COOPERATE": [30301, 18087],
                 "UC COLLABORATE": [30303, 18086], "UC COMMUNICATE": [30301, 0],
                 "business_trunking": [31027, 0]}
DID_GROUPS = {"ICASA": 24, "PORTEDNUMBERS": 35}
NUMBER_RANGES = ["2710133", "2712133", "2713133", "2714133", "2721133",
                 "2731393", "2741133", "2751133", "2787463", "2786"]
HGROUP = 0


def setup_logger(csv_path: str, site_name: str) -> logging.Logger:
    """Sets up logger that will be used to log all events happening in script.

        Parameters
        ----------
            csv_path : str
                Directory where the CSV file containing accounts info.
            site_name : str
                Name of the customer, as well site name.

        Returns
        -------
            Logger
                Logger to be used to keep logs of script information.
        """
    log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
    logging_name = csv_path + log_time + "_" + site_name
    logging.basicConfig(filename=logging_name + '.log',
                        filemode='a',
                        format='%(asctime)s, %(msecs)-3d ms || %(name)-22s ' +
                               '%(levelname)-5s ' +
                               '|| %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    logger = logging.getLogger("Full Import Logger")
    return logger


def set_credit_limit() -> int:
    """Get credit limit from user

    Returns
    -------
        int
            Credit limit set by user.
    """
    credit_limit = -1  # Set the site Credit limit here
    while credit_limit < 0:
        try:
            limit = int(input("Please enter credit limit: "))
            if str.upper(input(f"Proceed with a credit limit {limit} (yes/no)")) == "YES":
                credit_limit: int = limit
                print(f"Credit limit is {credit_limit}")
        except ValueError:
            print("Please enter a valid limit, digits only")

    return credit_limit


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
    login_api_url = "/Session/login"
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


def create_customer(access_token: str, **kwargs) -> int:
    """Create Clinix customer.

    Parameters
    ----------
        access_token: str
            Token required to make API requests.

    Returns
    -------
        int
            Returns the i_customer of recently created customer
    """

    customer_cloud_pbx_password = uuid.uuid4()
    customer_cloud_pbx_password = str(customer_cloud_pbx_password)[:15]
    customer_id = "zzz" + kwargs['site_name']

    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        customer_api_url = "/Customer/add_customer"
        customer_body = {
            "params": {
                "customer_info": {
                    "i_main_office": kwargs['i_main_office'],
                    "i_office_type": kwargs['office_type'],
                    "max_abbreviated_length": 4,
                    "inclusive_taxation": "N",
                    "out_date_format": "YYYY-MM-DD",
                    "i_template": None,
                    "password": customer_cloud_pbx_password,  # require UUID password generate here
                    "onetime_invoice_generation_enabled": 0,
                    "blocked": "N",
                    "billed_to": "2023-06-03 22:00:00",
                    "i_commission_plan": None,
                    "is_used": 0,
                    "bill_status": "O",
                    "name": customer_id,  # this is Site Name from CSV - Format: Customer_HQorRB_NAME_SAPCODE
                    "login": kwargs['site_name'].replace("_", "") + "login",  # this is Site Name from CSV without _
                    "i_role": 216,
                    "in_date_format": "YYYY-MM-DD",
                    "phone1": "",
                    "i_time_zone": 367,
                    "i_balance_control_type": 1,
                    "phone2": "",
                    "credit_exceed": 0,
                    "salutation": "",
                    "i_customer_type": 1,
                    "billing_lock": "N",
                    "callshop_enabled": "N",
                    "deactivate_on": None,
                    "country": "",
                    "generate_invoice_earlier": "N",
                    "invoice_generation_enabled": 0,
                    "firstname": "",
                    "iso_4217": "ZAR",
                    "suspension_delay_date": None,
                    "i_customer_class": 379,
                    "state": "",
                    "opening_balance": 0,
                    "has_custom_fields": 1,
                    "out_date_time_format": "YYYY-MM-DD HH24:MI:SS",
                    "i_lang": "en",
                    "bill_suspension_delayed": 0,
                    "address_line_2": "",
                    "zip": "",
                    "balance": 0,
                    "estimate_taxes": 0,
                    "ot_i_template": None,
                    "midinit": "",
                    "companyname": kwargs['site_name'],  # Format: Customer_HQorRB_NAME_SAPCODE, same as site name
                    "cont1": "",
                    "balance_transfer_allowed": "N",
                    "terminate_on": None,
                    "lastname": "",
                    "unallocated_payments": 0,
                    "perm_credit_limit": kwargs['credit_limit'],
                    "restore_on": None,
                    "city": "",
                    "i_ui_time_zone": 367,
                    "out_time_format": "HH24:MI:SS",
                    "cont2": "",
                    "service_features": [
                        {
                            "flag_value": "N",
                            "effective_flag_value": "N",
                            "name": "cli",
                            "attributes": [
                                {
                                    "effective_values": [
                                        None
                                    ],
                                    "name": "centrex",
                                    "values": [
                                        None
                                    ]
                                },
                                {
                                    "effective_values": [
                                        None
                                    ],
                                    "name": "display_number",
                                    "values": [
                                        None
                                    ]
                                },
                                {
                                    "effective_values": [
                                        "Y"
                                    ],
                                    "name": "display_number_check",
                                    "values": [
                                        "Y"
                                    ]
                                },
                                {
                                    "effective_values": [
                                        "N"
                                    ],
                                    "name": "display_name_override",
                                    "values": [
                                        "N"
                                    ]
                                },
                                {
                                    "effective_values": [
                                        "A"
                                    ],
                                    "name": "attest",
                                    "values": [
                                        "A"
                                    ]
                                },
                                {
                                    "effective_values": [
                                        None
                                    ],
                                    "name": "account_group",
                                    "values": [
                                        None
                                    ]
                                }
                            ]
                        },
                        {
                            "flag_value": "N",
                            "effective_flag_value": "N",
                            "name": "paging",
                            "attributes": [
                                {
                                    "effective_values": [
                                        "*33"
                                    ],
                                    "name": "paging_prefix",
                                    "values": [
                                        "*33"
                                    ]
                                }
                            ]
                        },
                        {
                            "flag_value": "N",
                            "effective_flag_value": "N",
                            "name": "endpoint_redirect",
                            "attributes": []
                        },
                        {
                            "flag_value": "3",
                            "effective_flag_value": "3",
                            "name": "rtpp_level",
                            "attributes": []
                        },
                        {
                            "flag_value": "Y",
                            "effective_flag_value": "Y",
                            "name": "music_on_hold",
                            "attributes": [
                                {
                                    "effective_values": [
                                        "1"
                                    ],
                                    "name": "i_moh",
                                    "values": [
                                        "1"
                                    ]
                                }
                            ]
                        },
                        {
                            "flag_value": "N",
                            "effective_flag_value": "N",
                            "name": "legal_intercept",
                            "attributes": []
                        },
                        {
                            "flag_value": "N",
                            "effective_flag_value": "N",
                            "name": "call_supervision",
                            "attributes": [
                                {
                                    "effective_values": [
                                        "*90"
                                    ],
                                    "name": "spy",
                                    "values": [
                                        "*90"
                                    ]
                                },
                                {
                                    "effective_values": [
                                        "0"
                                    ],
                                    "name": "spy_dtmf",
                                    "values": [
                                        "0"
                                    ]
                                },
                                {
                                    "effective_values": [
                                        "*91"
                                    ],
                                    "name": "whisper",
                                    "values": [
                                        "*91"
                                    ]
                                },
                                {
                                    "effective_values": [
                                        "1"
                                    ],
                                    "name": "whisper_dtmf",
                                    "values": [
                                        "1"
                                    ]
                                },
                                {
                                    "effective_values": [
                                        "*92"
                                    ],
                                    "name": "barge_in",
                                    "values": [
                                        "*92"
                                    ]
                                },
                                {
                                    "effective_values": [
                                        "2"
                                    ],
                                    "name": "barge_in_dtmf",
                                    "values": [
                                        "2"
                                    ]
                                }
                            ]
                        },
                        {
                            "flag_value": "N",
                            "effective_flag_value": "N",
                            "name": "sip_static_contact",
                            "attributes": [
                                {
                                    "effective_values": [
                                        "N"
                                    ],
                                    "name": "use_tcp",
                                    "values": [
                                        "N"
                                    ]
                                },
                                {
                                    "effective_values": [
                                        None
                                    ],
                                    "name": "user",
                                    "values": [
                                        None
                                    ]
                                },
                                {
                                    "effective_values": [
                                        None
                                    ],
                                    "name": "port",
                                    "values": [
                                        None
                                    ]
                                },
                                {
                                    "effective_values": [
                                        None
                                    ],
                                    "name": "host",
                                    "values": [
                                        None
                                    ]
                                }
                            ]
                        },
                        {
                            "flag_value": "N",
                            "effective_flag_value": "N",
                            "name": "bundle_discount",
                            "attributes": [
                                {
                                    "effective_values": [
                                        None
                                    ],
                                    "name": "i_bd_plan",
                                    "values": [
                                        None
                                    ]
                                }
                            ]
                        },
                        {
                            "flag_value": "~",
                            "effective_flag_value": "",
                            "name": "call_barring",
                            "attributes": [
                                {
                                    "effective_values": [],
                                    "name": "call_barring_rules",
                                    "values": []
                                }
                            ]
                        },
                        {
                            "flag_value": "N",
                            "effective_flag_value": "N",
                            "name": "cli_trust",
                            "attributes": [
                                {
                                    "effective_values": [
                                        "N"
                                    ],
                                    "name": "accept_caller",
                                    "values": [
                                        "N"
                                    ]
                                },
                                {
                                    "effective_values": [
                                        "N"
                                    ],
                                    "name": "supply_caller",
                                    "values": [
                                        "N"
                                    ]
                                }
                            ]
                        },
                        {
                            "flag_value": "N",
                            "effective_flag_value": "N",
                            "name": "distinctive_ring_vpn",
                            "attributes": []
                        },
                        {
                            "flag_value": "N",
                            "effective_flag_value": "N",
                            "name": "voice_quality",
                            "attributes": [
                                {
                                    "effective_values": [
                                        None
                                    ],
                                    "name": "i_vq_profile",
                                    "values": [
                                        None
                                    ]
                                }
                            ]
                        },
                        {
                            "flag_value": "N",
                            "effective_flag_value": "N",
                            "name": "first_login_greeting",
                            "attributes": []
                        },
                        {
                            "flag_value": "Y",
                            "effective_flag_value": "Y",
                            "name": "sim_calls_limit",
                            "attributes": [
                                {
                                    "effective_values": [
                                        "Y"
                                    ],
                                    "name": "restrict_on_net",
                                    "values": [
                                        "Y"
                                    ]
                                },
                                {
                                    "effective_values": [
                                        None
                                    ],
                                    "name": "max_calls_in",
                                    "values": [
                                        None
                                    ]
                                },
                                {
                                    "effective_values": [
                                        None
                                    ],
                                    "name": "max_bandwidth",
                                    "values": [
                                        None
                                    ]
                                },
                                {
                                    "effective_values": [
                                        None
                                    ],
                                    "name": "max_calls_out",
                                    "values": [
                                        None
                                    ]
                                },
                                {
                                    "effective_values": [
                                        None
                                    ],
                                    "name": "i_network_connectivity",
                                    "values": [
                                        None
                                    ]
                                },
                                {
                                    "effective_values": [
                                        None
                                    ],
                                    "name": "max_bandwidth_in",
                                    "values": [
                                        None
                                    ]
                                },
                                {
                                    "effective_values": [
                                        None
                                    ],
                                    "name": "max_bandwidth_out",
                                    "values": [
                                        None
                                    ]
                                },
                                {
                                    "effective_values": [
                                        None
                                    ],
                                    "name": "max_calls",
                                    "values": [
                                        None
                                    ]
                                },
                                {
                                    "effective_values": [
                                        None
                                    ],
                                    "name": "max_calls_fwd",
                                    "values": [
                                        None
                                    ]
                                }
                            ]
                        },
                        {
                            "flag_value": "N",
                            "effective_flag_value": "N",
                            "name": "permitted_sip_proxies",
                            "attributes": [
                                {
                                    "effective_values": [],
                                    "name": "proxies",
                                    "values": []
                                }
                            ]
                        },
                        {
                            "flag_value": "Y",
                            "effective_flag_value": "Y",
                            "name": "group_pickup",
                            "attributes": [
                                {
                                    "effective_values": [
                                        None
                                    ],
                                    "name": "group_pickup_note",
                                    "values": [
                                        None
                                    ]
                                }
                            ]
                        },
                        {
                            "flag_value": "Y",
                            "effective_flag_value": "Y",
                            "name": "voice_dialing",
                            "attributes": [
                                {
                                    "effective_values": [
                                        "Y"
                                    ],
                                    "name": "translate_cli_out",
                                    "values": [
                                        "Y"
                                    ]
                                },
                                {
                                    "effective_values": [
                                        "10238"
                                    ],
                                    "name": "i_dial_rule",
                                    "values": [
                                        "10238"
                                    ]
                                },
                                {
                                    "effective_values": [
                                        "N"
                                    ],
                                    "name": "translate_cli_in",
                                    "values": [
                                        "N"
                                    ]
                                },
                                {
                                    "effective_values": [
                                        "Y"
                                    ],
                                    "name": "translate_cld_in",
                                    "values": [
                                        "Y"
                                    ]
                                }
                            ]
                        },
                        {
                            "flag_value": "N",
                            "effective_flag_value": "N",
                            "name": "call_parking",
                            "attributes": [
                                {
                                    "effective_values": [
                                        "0"
                                    ],
                                    "name": "retrieval_timeout",
                                    "values": [
                                        "0"
                                    ]
                                },
                                {
                                    "effective_values": [
                                        "0"
                                    ],
                                    "name": "ringback_tone",
                                    "values": [
                                        "0"
                                    ]
                                },
                                {
                                    "effective_values": [
                                        "*70"
                                    ],
                                    "name": "park_prefix",
                                    "values": [
                                        "*70"
                                    ]
                                },
                                {
                                    "effective_values": [
                                        "*71"
                                    ],
                                    "name": "release_prefix",
                                    "values": [
                                        "*71"
                                    ]
                                }
                            ]
                        },
                        {
                            "flag_value": "N",
                            "effective_flag_value": "N",
                            "name": "voice_location",
                            "attributes": [
                                {
                                    "effective_values": [
                                        None
                                    ],
                                    "name": "allow_roaming",
                                    "values": [
                                        None
                                    ]
                                },
                                {
                                    "effective_values": [
                                        None
                                    ],
                                    "name": "primary_location",
                                    "values": [
                                        None
                                    ]
                                },
                                {
                                    "effective_values": [
                                        None
                                    ],
                                    "name": "primary_location_data",
                                    "values": [
                                        None
                                    ]
                                }
                            ]
                        }
                    ],
                    "suspend_on_insuff_funds": None,
                    "override_tariffs_enabled": "Y",
                    "in_time_format": "HH24:MI:SS",
                    "service_flags": "Y         3       Y",
                    "note": "",
                    "i_billing_period": 4,
                    "purge_after_months": None,
                    "faxnum": "",
                    "i_acl": 136,
                    "baddr1": "",
                    "credit_limit": kwargs['credit_limit']
                }
            }
        }

        t1_start = process_time()
        response = requests.post(customer_api_url, json=customer_body, headers=headers, verify=False)
        t1_stop = process_time()
        turnaround_time = round((t1_stop - t1_start) * 1000)

        if response.status_code == 500:
            response.raise_for_status()

        print(f'Create Customer:  response_code={response.status_code}, turnaround_time: {turnaround_time}ms')
        return response.json()['i_customer']

    except requests.exceptions.HTTPError:
        print("An error occurred while creating the customer.")
        sys.exit(1)


def get_accounts_info(csv_path: str, site_name: str) -> list[dict]:
    """
    Parameters
    ----------
        csv_path : str
            Directory where the CSV file containing accounts info.
        site_name : str
            Name of the customer, as well site name.

    Returns
    -------
        list[dict]
            a List containing all accounts for the customer
    """
    accounts: list[dict] = []

    with open(csv_path + site_name + ".csv", "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            row: dict
            accounts.append(row)

    return accounts


def create_accounts(access_token: str, logger: logging.Logger, i_customer: int, accounts_info: list[dict],
                    site_name: str) -> list[list[int | str]]:
    acc_ext_info: list[list[int | str]] = []
    for account in accounts_info:
        ecn_info: list[str | int] = []
        i_account = add_sip_account(access_token, i_customer, account)
        logger.info(f"SIP account created, i_account: {i_account}")

        if account["extension"] != "":
            i_c_ext = create_extension(access_token, i_account, i_customer, account)
            logger.info(f"Added Extension to i_customer {i_customer} and i_account {i_account}, i_c_ext: {i_c_ext}")

        recep = str(account["firstName"]) + "." + str(account["lastName"])
        recep = recep.lower()

        if recep.find("reception") >= 0:
            result = add_to_reception_huntgroup(access_token, logger, i_customer, i_account, i_c_ext, site_name)
            logger.info(f"Adding receptionist to hunt group: {result}")

        if account["phoneNumber"]:
            i_did_number = add_did_number(access_token, i_customer, i_account, account, site_name)
            logger.info(f"Add DID to PortaOne platform, i_did_number: {i_did_number}")
            logger.info(f"Add DID to i_customer {i_customer}")
            logger.info(f"Add DID to i_master_account {i_account}")

        ecn_info.append(i_customer)
        ecn_info.append(account["extension"])
        ecn_info.append(account["accessDeviceEndpoint.accessDevice.macAddress"])
        ecn_info.append(account["firstName"])
        ecn_info.append(account["lastName"])

        acc_ext_info.append(ecn_info)

    return acc_ext_info


def add_sip_account(access_token: str, i_customer: int, account_info: dict) -> int:
    """Add SIP Account to PortaOne

    Parameters
    ----------
        access_token : str
            Token required to make API requests.
        i_customer : int
            Name of the customer, as well site name.
        account_info : dict
            Name of the customer, as well site name.

    Returns
    -------
        list[dict]
            a List containing all accounts for the customer
    """
    ext_name = "ph" + str(i_customer) + "x" + account_info["extension"]
    firstname: str = account_info["firstName"]

    i_account_role = 1
    lastname = account_info["lastName"]
    cli = account_info["callingLineIdPhoneNumber"]
    if cli == "":
        cli = account_info["phoneNumber"]
        if account_info["phoneNumber"] == "":
            cli = "27999999999"

    email = account_info["impId"]

    if firstname == 'pilot':
        i_account_role = 6
        ext_name = input(f"Please enter {firstname} {lastname}'s IP: ")
        i_product = 24683
        i_subscription = 0
    else:
        i_product = PROD_SUB_SETS[account_info["servicePacks"]][0]
        i_subscription = PROD_SUB_SETS[account_info["servicePacks"]][1]

    sip_account_password = uuid.uuid4()
    sip_account_password = str(sip_account_password)[:15]
    add_sip_account_api_url = "/Account/add_account"
    add_sip_account_headers = {"Authorization": f"Bearer {access_token}"}
    add_sip_account_body = {
        "params": {
            "account_info": {
                "billing_model": 1,
                "email": email,
                "h323_password": sip_account_password,
                "i_account_role": i_account_role,
                "i_customer": i_customer,
                "i_product": i_product,  # 21322 onboarding product
                "id": ext_name,  # this will be ph+icust+x+ext
                "firstname": firstname,  # Firstname from CSV
                "lastname": lastname,  # Lastname from CSV
                "service_features": [{
                    "attributes": [
                        {
                            "effective_values": [
                                cli
                            ],
                            "name": "centrex",
                            "values": [
                                cli
                            ]
                        },
                        {
                            "effective_values": [
                                cli
                            ],
                            "name": "display_number",
                            "values": [
                                cli
                            ]
                        }
                    ],
                    "effective_flag_value": "Y",
                    "flag_value": "Y",
                    "locked": 0,
                    "locks": [],
                    "name": "cli"
                }]
            }
        }
    }

    t1_start = process_time()
    sip_account_response = requests.post(add_sip_account_api_url, json=add_sip_account_body,
                                         headers=add_sip_account_headers, verify=False)
    t1_stop = process_time()
    turnaround_time = round((t1_stop - t1_start) * 1000)

    print(
        f'Create Account:  response_code={sip_account_response.status_code}, '
        f'turnaround_time: {turnaround_time}ms')
    print(sip_account_response.json())

    if i_subscription != 0:
        add_subscription_to_acc(access_token, sip_account_response.json()['i_account'], i_subscription)

    return sip_account_response.json()['i_account']


def add_subscription_to_acc(access_token: str, i_account: int, i_subscription: int) -> bool:
    """Add SIP Account to PortaOne

    Parameters
    ----------
        access_token : str
            Token required to make API requests.
        i_account : int
            Unique identifier of account.
        i_subscription : int
            Unique identifier of subscription to be added to account.

    Returns
    -------
        bool
            True if subscription was successfully answered
    """
    add_subscription_url = "/Account/add_subscription"
    add_subscription_header = {"Authorization": f"Bearer {access_token}"}
    add_subscription_body = {
        "params": {
            "i_account": i_account,
            "subscription_info": {
                "i_subscription": i_subscription
            }
        }
    }
    t1_start = process_time()
    response = requests.post(add_subscription_url, headers=add_subscription_header,
                             json=add_subscription_body,
                             verify=False)
    t1_stop = process_time()
    turnaround_time = round((t1_stop - t1_start) * 1000)

    print(
        f'Added Subscription: response_code={response.status_code}, turnaround_time:'
        f'{turnaround_time}ms')

    return True


def create_extension(access_token: str, i_account: int, i_customer: int, account_info: dict) -> int:
    """Add SIP Account to PortaOne

    Parameters
    ----------
        access_token : str
            Token required to make API requests.
        i_account : int
            Unique identifier of account.
        i_customer : int
            Unique identifier of subscription to be added to account.
        account_info : dict
            Name of the customer, as well site name.

    Returns
    -------
        int
            Unique identifier of the created extension.
    """
    add_customer_extension_api_url = "/Customer/add_customer_extension"
    add_customer_extension_headers = {"Authorization": f"Bearer {access_token}"}
    add_customer_extension_body = {
        "params": {
            "i_account": i_account,  # this is the i_account variable written to the console on API add_account
            "i_customer": i_customer,  # i_customer number retrieved from customer create api call
            "id": account_info["extension"],  # this is the extension number
            "name": account_info["firstName"] + "." + account_info["lastName"]
        }
    }

    t1_start = process_time()
    add_customer_extension_response = requests.post(add_customer_extension_api_url,
                                                    json=add_customer_extension_body,
                                                    headers=add_customer_extension_headers, verify=False)
    t1_stop = process_time()
    turnaround_time = round((t1_stop - t1_start) * 1000)

    print(
        f'Add Customer Extension response:  response_code={add_customer_extension_response.status_code},'
        f' turnaround_time: {turnaround_time}ms')

    if add_customer_extension_response.status_code == 500:
        pass

    return add_customer_extension_response.json()['i_c_ext']


def add_did_number(access_token: str, i_customer: int, i_account: int, account_info: dict, site_name: str) -> int:
    """Add SIP Account to PortaOne

    Parameters
    ----------
        access_token : str
            Token required to make API requests.
        i_customer : int
            Unique identifier of the customer.
        i_account : int
            Unique identifier of the account.
        account_info : dict
            Name of the customer, as well site name.
        site_name : str
            The actual number of the did, in 164 format.

    Returns
    -------
        int
            Unique identifier of the added did.
    """
    # region Add DID to Platform
    i_group = 35
    for numRange in NUMBER_RANGES:
        range_index = account_info["phoneNumber"].find(numRange)
        if range_index == 0:
            i_group = 24

    add_did_api_url = "/DID/add_number"
    add_did_headers = {"Authorization": f"Bearer {access_token}"}
    add_did_body = {
        "params": {
            "number_info": {
                "activation_cost": 0.0,
                "activation_fee": 0.0,
                "activation_revenue": 0.0,
                "country_iso": "ZA",
                "country_name": "South Africa",
                "periodic_fee": 0.0,
                "recurring_cost": 0.0,
                "vendor_batch_name": "Gijima SBC Test",
                "external": 1,
                "free_of_charge": "N",
                "i_dv_batch": 114,
                "i_do_batch": 147,
                "i_group": i_group,
                "i_vendor": 152,
                "is_used": 1,
                "iso_4217": "ZAR",
                "frozen": "N",
                # //variables apply to the below
                "description": site_name,
                # // i would like to have the Branchname as the description of the DID
                #  IE Br_CapeTown_0800 from the csv
                "number": account_info["phoneNumber"]
                # //this is the actual DID number is 164 format I want to variable this from CSV
            }
        }
    }

    print(f'Add DID Body: {add_did_body}')

    t1_start = process_time()
    add_did_response = requests.post(add_did_api_url,
                                     json=add_did_body,
                                     headers=add_did_headers, verify=False)
    t1_stop = process_time()
    turnaround_time = round((t1_stop - t1_start) * 1000)

    print(
        f'Add DID response:  response_code={add_did_response.status_code}, turnaround_time: '
        f'{turnaround_time}ms')

    i_did_number = add_did_response.json()['i_did_number']
    # endregion

    # region Assign DID to customer
    assign_did_api_url = "/DID/assign_did_to_customer"
    assign_did_headers = {"Authorization": f"Bearer {access_token}"}
    assign_did_body = {
        "params": {
            "i_customer": i_customer,
            # //this variable will be the sites/branch customer we created for the branch
            "i_did_number": i_did_number
            # //the i_did_nr will be created in the previous call where we will capture the
            # DID for the extension or Huntgroup from CSV
        }
    }

    t1_start = process_time()
    assign_did_response = requests.post(assign_did_api_url,
                                        json=assign_did_body,
                                        headers=assign_did_headers, verify=False)
    t1_stop = process_time()
    turnaround_time = round((t1_stop - t1_start) * 1000)

    print(
        f'Assign DID response:  response_code={assign_did_response.status_code}, turnaround_time: '
        f'{turnaround_time}ms')
    # endregion

    # region Assign DID to account
    add_account_did_url = "/DID/assign_did_to_account"
    add_account_did_header = {"Authorization": f"Bearer {access_token}"}
    add_account_did_body = {
        "params": {
            "i_did_number": i_did_number,  # The unique ID of the DID number record
            "i_master_account": i_account  # The unique ID of the account this DID number is assigned to
        }
    }

    t1_start = process_time()
    add_account_did_response = requests.post(add_account_did_url,
                                             json=add_account_did_body,
                                             headers=add_account_did_header, verify=False)
    t1_stop = process_time()
    turnaround_time = round((t1_stop - t1_start) * 1000)
    print(
        f'Assign DID response:  response_code={add_account_did_response.status_code}, turnaround_time: '
        f'{turnaround_time}ms')
    # endregion

    return i_did_number


def load_ecn_data_to_file(ecn_data: list[list[int | str]], file_path: str, site_name: str,
                          logger: logging.Logger) -> str:
    """Create a reception hunt group that all reception SIP accounts will be in.

    Parameters
    ----------
        ecn_data : list[list[int | str]]
            Data gathered for ECN usage
        file_path : str
            Path to file where data will be stored.
        logger : logging.Logger
            Used to keep logs of events in script.
        site_name : str
            The actual number of the did, in 164 format.

    Returns
    -------
        bool
            True if reception extension added to hunt group.
    """
    ecn_file: str
    with open(file_path + site_name + '_phAccount.csv', 'a', newline='') as phAccountCSV:
        csv_writer = csv.writer(phAccountCSV)
        csv_writer.writerow(['i_customer', 'extension',
                             'accessDeviceEndpoint.accessDevice.macAddress',
                             'firstName',
                             'lastName'])
        csv_writer.writerows(ecn_data)
        ecn_file = phAccountCSV.name
        logger.info(f"Added sip accounts to csv file: {ecn_file}")

    return ecn_file


def add_to_reception_huntgroup(access_token: str, logger: logging.Logger, i_customer: int, i_account: int, i_c_ext: int,
                               site_name: str) -> bool:
    """Create a reception hunt group that all reception SIP accounts will be in.

    Parameters
    ----------
        access_token : str
            Token required to make API requests.
        logger : logging.Logger
            Used to keep logs of events in script.
        i_customer : int
            Unique identifier of the customer.
        i_account : int
            Unique identifier of the account.
        i_c_ext : int
            Unique identifier of the account ex.
        site_name : str
            The actual number of the did, in 164 format.

    Returns
    -------
        bool
            True if reception extension added to hunt group.
    """
    global HGROUP
    if HGROUP == 0:
        HGROUP = create_reception_huntgroup(access_token, i_customer, site_name)
        logger.info(f"Created Hunt group for Receptionists, i_c_group: {HGROUP}")

    update_huntgroup_url = "/Customer/update_customer_huntgroup"
    update_huntgroup_header = {"Authorization": f"Bearer {access_token}"}
    update_huntgroup_body = {
        "params": {
            "add_extensions": [
                {
                    "account_id": i_account,
                    "i_c_ext": i_c_ext
                }
            ],
            "i_c_group": HGROUP
        }
    }

    t1_start = process_time()
    update_huntgroup_response = requests.post(update_huntgroup_url,
                                              json=update_huntgroup_body,
                                              headers=update_huntgroup_header, verify=False)
    t1_stop = process_time()
    turnaround_time = round((t1_stop - t1_start) * 1000)

    print(
        f'Add Extension to Hunt Group response:  response_code={update_huntgroup_response.status_code},'
        f' turnaround_time: {turnaround_time}ms')
    print(update_huntgroup_response.json())

    logger.info(f"Added i_account {i_account} i_c_ext {i_c_ext} to i_c_group {HGROUP}")

    return True


def create_reception_huntgroup(access_token: str, i_customer: int, site_name: str) -> int:
    """Create a reception hunt group that all reception SIP accounts will be in.

    Parameters
    ----------
        access_token : str
            Token required to make API requests.
        i_customer : int
            Unique identifier of the customer.
        site_name : str
            The actual number of the did, in 164 format.

    Returns
    -------
        int
            Unique identifier of the added did.
    """
    create_huntgroup_url = "/Customer/add_customer_huntgroup"
    create_huntgroup_header = {"Authorization": f"Bearer {access_token}"}
    create_huntgroup_body = {
        "params": {
            "activity_monitoring": "N",
            "call_wrap_up_time": 0,
            "hunt_keep_original_cli": "Y",
            "hunt_sequence": "Simultaneous",
            "hunt_while_wrapping_up": "always",
            "i_customer": i_customer,
            "id": "99999",  # Get clarification about id for customers
            "minimal_served_call_duration": 0,
            "name": site_name,  # Get customer hunt group name for receptionist
            "pickup_allowed": "Y",
            "wrap_up_extend_time": 0,
            "wrap_up_passed_calls": "N"
        }
    }

    t1_start = process_time()
    response = requests.post(create_huntgroup_url, headers=create_huntgroup_header,
                             json=create_huntgroup_body, verify=False)
    t1_stop = process_time()
    turnaround_time = round((t1_stop - t1_start) * 1000)
    i_c_group = response.json()['i_c_group']

    print(response.status_code)
    print(turnaround_time)

    return i_c_group


def main():
    file_path = filedialog.askopenfilename()
    slash_index: int = file_path.rfind('/') + 1
    site_name = file_path[slash_index:-4]
    csv_path = file_path[:slash_index]

    logger = setup_logger(csv_path, site_name)
    #
    # credit_limit = set_credit_limit()
    # logger.info(f"Credit limit has been set to: {credit_limit}")

    access_token = get_access_token(USERNAME, TOKEN)
    logger.info(f"Login successful, access token: {access_token}")

    # i_customer = create_customer(access_token,
    #                              i_main_office=0, office_type=3,
    #                              site_name=site_name, credit_limit=credit_limit)
    # print(f'Customer ID:  i_customer={i_customer}')
    # logger.info(f"Customer created, i_customer: {i_customer}")

    accounts_info = get_accounts_info(csv_path, site_name)
    logger.info(f"Accounts' information retrieved from CSV file.")

    ecn_info = create_accounts(access_token, logger, 15233, accounts_info, site_name)

    ecn_file = load_ecn_data_to_file(ecn_info, csv_path, site_name, logger)


if __name__ == "__main__":
    main()
