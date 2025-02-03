import csv
import logging
import os
import sys
import uuid
from getpass import getpass

import requests

from datetime import datetime
from dotenv import load_dotenv
from time import process_time
from tkinter import filedialog

URL = "/"

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = "Add_multiple_Customers_" + str(log_time)
logging.basicConfig(filename=logging_name + '.log',
                    filemode='a',
                    format='%(asctime)s, %(msecs)-3d ms || %(name)-22s ' +
                           '%(levelname)-5s ' +
                           '|| %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.NOTSET)
logger = logging.getLogger("Full Import Logger")

# endregion

PROD_SUB_SETS = {"UC Connect": [11649, 0], "UC Cooperate": [11649, 18087],
                 "UC Collaborate": [18984, 18086], "UC Communicate": [11649, 0],
                 "Business Trunk": [31025, 0]}  # Basic = Connect, Mobillty = Collaborate
DID_GROUPS = {"ICASA": 24, "PORTEDNUMBERS": 35}
NUMBER_RANGES = ["2710133", "2712133", "2713133", "2714133", "2721133",
                 "2731393", "2741133", "2751133", "2787463", "2786"]
PINCODE_PROD_CODE = 29158
CUSTOM_FIELDS = [706, 820]

phAccountList: list[list[str]] = []
i_c_group = 0


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

    access_token = response.json()['access_token']

    return access_token


def get_customers_info() -> dict[str, list[dict]]:
    """Retrieves accounts' information from CSV file and groups
    them by the site that they are assigned to.

    :return: Customer-Accounts lists
    """
    customer_sets: dict[str, list[dict]] = {}
    csv_customers_data: list[dict] = []
    with open(filedialog.askopenfilename(), "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for entry in csv_reader:
            entry: dict
            csv_customers_data.append(entry)

    for account in csv_customers_data:
        if not customer_sets[account["group_id"]]:
            customer_sets[account["group_id"]] = []
        customer_sets[account["group_id"]].append(account)

    return customer_sets


def create_customer(token: str, customer_name: str) -> int:
    """Creates a customer with the given site name as the customer id.

    :param token: The session ID used to make requests to the PortaOne API.
    :param customer_name: Name of the site that the customer instance is created for.
    :return: The unique numeral id of the created customer site.
    """
    i_customer: int = 0
    credit_limit = 100000
    customer_cloud_pbx_password = uuid.uuid4()
    customer_cloud_pbx_password = str(customer_cloud_pbx_password)[:15]
    customer_id = "zzz" + customer_name
    office_type = 3

    headers = {"Authorization": f"Bearer {token}"}
    customer_api_url = "/Customer/add_customer"
    customer_body = {
        "params": {
            "customer_info": {
                #  "i_main_office": i_main_office,
                "i_office_type": office_type,
                "bcc": "d1aeffad.gijima.com@emea.teams.ms,chris.terblanche@gijima.com",
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
                "login": customer_name.replace("_", "") + "login_new",  # this is Site Name from CSV without _
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
                "companyname": customer_name,  # Format: Customer_HQorRB_NAME_SAPCODE, same as site name
                "cont1": "",
                "balance_transfer_allowed": "N",
                "terminate_on": None,
                "lastname": "",
                "unallocated_payments": 0,
                "perm_credit_limit": credit_limit,
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
                "credit_limit": credit_limit
            }
        }
    }

    response = requests.post(url=customer_api_url, headers=headers,
                             json=customer_body, verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    return i_customer


def add_sip_account(token: str, i_customer: int, account_list: list[dict]) -> bool:
    """ Creates SIP accounts on the given customer site.

    :param token: The session ID used to make requests to the PortaOne API.
    :param i_customer: The unique numeral id of the created customer site.
    :param account_list: The information of all accounts that will be created for the
     given customer site.
    :return: Indicates whether account creation was successful.
    """
    prod_sub_count = {11649: 0, 18984: 0}
    ph_account_list: list[list[str]] = []
    site_name = ""

    add_sip_account_api_url = "/Account/add_account"
    add_sip_account_headers = {"Authorization": f"Bearer {token}"}
    for acc in account_list:
        sip_account_password = uuid.uuid4()
        sip_account_password = str(sip_account_password)[:15]
        product = PROD_SUB_SETS[acc["service_pack"]][0]
        subscription = PROD_SUB_SETS[acc["service_pack"]][1]
        ext_name = f"ph{i_customer}x{acc['extension']}"
        firstname = acc["firstName"]
        lastname = acc["lastName"]
        email = acc["email"]  # Check what name the column will be for email addresses

        add_sip_account_body = {
            "params": {
                "account_info": {
                    "billing_model": 1,
                    "email": email,
                    "h323_password": sip_account_password,
                    "i_customer": i_customer,
                    "i_product": product,  # 21322 onboarding product
                    "id": ext_name,  # this will be ph+icust+x+ext
                    "firstname": firstname,  # Firstname from CSV
                    "lastname": lastname  # Lastname from CSV
                }
            }
        }

        response = requests.post(url=add_sip_account_api_url, headers=add_sip_account_headers,
                                 json=add_sip_account_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        i_account = response.json()['i_account']
        logger.info(f"Account {i_account} created.")

        ph_account_list.append([ext_name, str(i_account), acc["extension"]])
        prod_sub_count[product] += 1

        if subscription != 0:
            add_acc_sub(token, i_account, subscription)

        add_custom_fields(token, i_account, acc["yahooId"], acc["departmentName"])

        add_extension(token, acc["extension"], i_customer, i_account, firstname, lastname)

        add_did(token, acc["phoneNumber"], i_customer, i_account, acc["groupId"])
        site_name = acc["groupId"]

    update_agreement(token, i_customer, prod_sub_count)
    with open(site_name + '_phAccount.csv', 'a', newline='') as phAccountCSV:
        csv_writer = csv.writer(phAccountCSV)
        csv_writer.writerow(['phName', 'phAccounts', 'extensions'])
        csv_writer.writerows(ph_account_list)
        logger.info(f"Added sip accounts to csv file: {phAccountCSV.name}")

    return True


def update_agreement(token: str, i_customer: int, prod_sub_count: dict[int, int]) -> bool:
    """Updates the agreement value of a customer site with the correct amounts of each product
    that have been allocated to the SIP accounts

    :param token: The session ID used to make requests to the PortaOne API.
    :param i_customer: The unique numeral id of the created customer site.
    :param prod_sub_count: Product ID and amount of that product assigned to SIP accounts.
    :return: Indicates whether agreement update was successful.
    """
    update_agreement_info_url = "/Customer/update_agreement_conditions"
    update_agreement_info_header = {"Authorization": f"Bearer {token}"}
    update_agreement_info_body = {
        "params": {
            "i_customer": i_customer,
            "agreement_condition_list": []
        }
    }

    # region Check which agreements need to be added to body
    if prod_sub_count[11649] > 0:
        collab_agreements: dict = {"i_product": 18984,
                                   "max_offered_quantity": prod_sub_count[11649]
                                   }
        update_agreement_info_body['params']['agreement_condition_list'].append(collab_agreements)
    if prod_sub_count[18984] > 0:
        collab_agreements: dict = {"i_product": 11649,
                                   "max_offered_quantity": prod_sub_count[18984]
                                   }
        update_agreement_info_body['params']['agreement_condition_list'].append(collab_agreements)
    # endregion

    if update_agreement_info_body['params']['agreement_condition_list']:
        response = requests.post(update_agreement_info_url, headers=update_agreement_info_header,
                                 json=update_agreement_info_body, verify=False)

        if response.status_code == 500:
            logger.error("An Error Occurred: " + str(response.json()))
            input("An Error Occurred. Check Log.")
            sys.exit(1)

        logger.info(f"Updated agreements of i_customer {i_customer}")

    return True


def add_did(token: str, did: str, i_customer: int, i_account: int, site_name: str) -> bool:
    """Adds DID to PortaOne platform, assigns it to the given customer, and adds it as a
    alias to the given SIP account.

    :param site_name: The name of the Customer site.
    :param token: The session ID used to make requests to the PortaOne API.
    :param did: The number that will be added to the PortaOne Platform, in E.164 format.
    :param i_customer: The unique numeral id of the created customer site.
    :param i_account: The unique numeral id of a SIP account.
    :return: Indicates whether the assignment of the DID was successful.
    """
    i_group = 35
    for numRange in NUMBER_RANGES:
        range_index = did.find(numRange)
        if range_index == 0:
            i_group = 24

    add_did_api_url = "/DID/add_number"
    add_did_headers = {"Authorization": f"Bearer {token}"}
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
                "vendor_batch_name": "",
                "external": 1,
                "free_of_charge": "N",
                "i_dv_batch": 114,
                "i_do_batch": 147,
                "i_group": i_group,
                "i_vendor": 152,
                "is_used": 1,
                "iso_4217": "ZAR",
                "frozen": "N",
                "description": site_name,
                "number": did
                # //this is the actual DID number is 164 format I want to variable this from CSV
            }
        }
    }

    response = requests.post(url=add_did_api_url, headers=add_did_headers,
                             json=add_did_body, verify=False)
    i_did_number = response.json()["i_did_number"]

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    logger.info(f"DID {did} added to Platform.")

    assign_did_api_url = "/DID/assign_did_to_customer"
    assign_did_headers = {"Authorization": f"Bearer {token}"}
    assign_did_body = {
        "params": {
            "i_customer": i_customer,
            # //this variable will be the sites/branch customer we created for the branch
            "i_did_number": i_did_number
            # //the i_did_nr will be created in the previous call where we will capture the
            # DID for the extension or Huntgroup from CSV
        }
    }

    response = requests.post(url=assign_did_api_url, headers=assign_did_headers,
                             json=assign_did_body, verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    logger.info(f"Add DID to i_customer {i_customer}")

    add_account_did_url = "/DID/assign_did_to_account"
    add_account_did_header = {"Authorization": f"Bearer {token}"}
    add_account_did_body = {
        "params": {
            "i_did_number": i_did_number,  # The unique ID of the DID number record
            "i_master_account": i_account  # The unique ID of the account this DID number is assigned to
        }
    }

    response = requests.post(url=add_account_did_url, headers=add_account_did_header,
                             json=add_account_did_body, verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    logger.info(f"DID {did} add as alias to account Account {i_account}.")
    return True


def add_extension(token: str, extension: str, i_customer: int, i_account: int, first_name: str, last_name: str) -> bool:
    """Creates a cloud PBK extension for the given SIP account.

    :param token: The session ID used to make requests to the PortaOne API.
    :param extension: The extension number assigned to the SIP account.
    :param i_customer: The unique numeral id of the customer.
    :param i_account: the unique numeral id of the account.
    :param first_name: The first name belonging to the given account.
    :param last_name: The last name belonging to the given account.
    :return: Indicates whether extension creation was successful.
    """
    add_customer_extension_api_url = "/Customer/add_customer_extension"
    add_customer_extension_headers = {"Authorization": f"Bearer {token}"}
    add_customer_extension_body = {
        "params": {
            "i_account": i_account,  # this is the i_account variable written to the console on API add_account
            "i_customer": i_customer,  # i_customer number retrieved from customer create api call
            "id": extension,  # this is the extension number
            "name": first_name + "." + last_name
            # //this is Firstname.Lastname from CSV for extension name on cloudpbx
        }
    }

    response = requests.post(url=add_customer_extension_api_url, headers=add_customer_extension_headers,
                             json=add_customer_extension_body, verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    logger.info(f"Extension {response.json()['i_c_ext']} added to Customer {i_customer} for Account {i_account}")
    return True


def add_acc_sub(token: str, i_account: int, i_subscription: int) -> bool:
    """Add a subscription to a given account.

    :param token: The session ID used to make requests to the PortaOne API.
    :param i_account: The unique numeral id of the account.
    :param i_subscription: the unique numeral id of the subscription.
    :return: Indicates whether subscription assignment was successful.
    """
    add_subscription_url = "/Account/add_subscription"
    add_subscription_header = {"Authorization": f"Bearer {token}"}
    add_subscription_body = {
        "params": {
            "i_account": i_account,
            "subscription_info": {
                "i_subscription": i_subscription
            }
        }
    }

    response = requests.post(url=add_subscription_url, headers=add_subscription_header,
                             json=add_subscription_body, verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    logger.info(f"Subscription {i_subscription} added to Account {i_account}")

    return True


def add_custom_fields(token: str, i_account: int, cost_center, department) -> bool:
    """Adds and updates customer fields to a given account.

    :param token: The session ID used to make requests to the PortaOne API.
    :param i_account: The unique numeral id of the account.
    :param cost_center: The cost center code that will be assigned to the account.
    :param department: The department name that will be assigned to the account.
    :return: Indicates whether custom field assignment was successful.
    """
    update_custom_fields_url = "/Account/update_custom_fields_values"
    update_custom_fields_header = {"Authorization": f"Bearer {token}"}
    update_custom_fields_body = {
        "params": {
            "custom_fields_values": [
                {
                    "db_value": cost_center,
                    "name": "Cost Center"
                },
                {
                    "db_value": department,
                    "name": "Department",
                }
            ],
            "i_account": i_account
        }
    }

    response = requests.post(url=update_custom_fields_url, headers=update_custom_fields_header,
                             json=update_custom_fields_body, verify=False)

    if response.status_code == 500:
        logger.error("An Error Occurred: " + str(response.json()))
        input("An Error Occurred. Check Log.")
        sys.exit(1)

    logger.info(f"Custom fields added to Account {i_account}")

    return True


def main():
    print("-----------------------------------------------------------")
    print("Add multiple customers to PortaOne with a single CSV file.")
    print("-----------------------------------------------------------")

    usern = input("Username: ")
    passw = getpass("Password: ")

    token = get_access_token(usern, passw)

    customer_sets = get_customers_info()

    for site_name, value in customer_sets.items():
        i_customer = create_customer(token, site_name)
        add_sip_account(token, i_customer, value)
        logger.info(f"Customer and Accounts Added")

    input("Operation Complete.")
    sys.exit(0)


if __name__ == "__main__":
    main()
