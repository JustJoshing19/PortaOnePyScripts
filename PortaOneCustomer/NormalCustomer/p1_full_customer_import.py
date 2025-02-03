import csv
import logging
import requests
import uuid

from datetime import datetime
from time import process_time
from tkinter import filedialog

# Contains the product/subscription combination for each main product
PROD_SUB_SETS = {"UC Connect": [11649, 0], "UC Cooperate": [11649, 18087],
                 "UC Collaborate": [18984, 18086], "UC Communicate": [11649, 0],
                 "business trunk": [31025, 0]} # Basic = Connect, Mobillty = Collaborate
DID_GROUPS = {"ICASA": 24, "PORTEDNUMBERS": 35}
NUMBER_RANGES = ["2710133", "2712133", "2713133", "2714133", "2721133",
                 "2731393", "2741133", "2751133", "2787463", "2786"]
PINCODE_PROD_CODE = 29158
CUSTOM_FIELDS = [706, 820]

prod_sub_count = {11649: 0, 18984: 0}
phAccountList: list[list[str]] = []
i_c_group = 0

# region Get file path and name
file_path = filedialog.askopenfilename()

slashIndex: int = file_path.rfind('/') + 1

siteName = file_path[slashIndex:-4]
csv_path = file_path[:slashIndex]

huntgroupName = "HG_" + siteName
# endregion

# region Set up logger
log_time = datetime.strftime(datetime.now(), '%d-%m-%Y_%H-%M-%S')
logging_name = csv_path + log_time + "_" + siteName
logging.basicConfig(filename=logging_name + '.log',
                    filemode='a',
                    format='%(asctime)s, %(msecs)-3d ms || %(name)-22s ' +
                           '%(levelname)-5s ' +
                           '|| %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger("Full Import Logger")
# endregion

# region Get credit limit from user
credit_limit = -1  # Set the site Credit limit here
while credit_limit < 0:
    try:
        limit = int(input("Please enter credit limit: "))
        if str.upper(input(f"Proceed with a credit limit {limit} (yes/no)")) == "YES":
            credit_limit: int = limit
            print(f"Credit limit is {credit_limit}")
            logger.info(f"Credit limit has been set to: {credit_limit}")
    except ValueError as e:
        print("Please enter a valid limit, digits only")
# endregion

# region Request office type information that is required
# add branch/HQ info here needs to be added - does the customer use extension dialling between sites
officeType = 0  # 1 - none; 2 - branch_office; 3 - main_office.
i_main_office = 0  # If branch have them provide main branch i_customer id

userInput = input("Is this site a branch office (RB) or the main office (HQ) ?: ")
userInput = str.upper(userInput.strip())

mainOffice = ["HQ", "HEADQUARTERS", "MAIN OFFICE"]
branchOffice = ["RB", "BRANCH OFFICE"]

while officeType == 0:
    if userInput in mainOffice:
        officeType = 3
        logger.info(f"{siteName} is the HQ")

    elif userInput in branchOffice:
        while officeType == 0:
            try:
                i_main_office = int(input("Please enter the ID of the main office for this branch: "))
                print(f"Main office id is {i_main_office}")
                officeType = 2
                logger.info(f"{siteName} is regional branch, HQ i_customer id: {i_main_office}")
            except ValueError as e:
                print("Please enter a valid customer id, only digits.")
    else:
        userInput = input("Invalid input please use:\n"
                          "'HQ', 'headquarters' or 'main office' to indicate Main Office\n"
                          "'RB' or 'branch office' to indicate Main Office\n\n"
                          "Is this site a branch office (RB) or the main office (HQ) ?: ")
        userInput = str.upper(userInput.strip())
# endregion

# region Log in & get access_token
login_api_url = "/Session/login"
login_body = {'params': {'login': 'chris_admin', 'token': ''}}
t1_start = process_time()
response = requests.post(login_api_url, json=login_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
# endregion

if response.status_code == 200:
    access_token = response.json()['access_token']
    logger.info(f"Login successful, access token: {access_token}")
    expires_at = response.json()['expires_at']
    print(f'Login Successful! expires_at: {expires_at}, turnaround_time: {turnaround_time}ms')

    customer_cloudPBX_Password = uuid.uuid4()
    customer_cloudPBX_Password = str(customer_cloudPBX_Password)[:15]
    customer_id = "zzz" + siteName

    # region 1. Create customer - currently not specifying branch/HQ info
    headers = {"Authorization": f"Bearer {access_token}"}
    customer_api_url = "/Customer/add_customer"
    customer_body = {
        "params": {
            "customer_info": {
                "i_main_office": i_main_office,
                "i_office_type": officeType,
                "max_abbreviated_length": 4,
                "inclusive_taxation": "N",
                "out_date_format": "YYYY-MM-DD",
                "i_template": None,
                "password": customer_cloudPBX_Password,  # require UUID password generate here
                "onetime_invoice_generation_enabled": 0,
                "blocked": "N",
                "billed_to": "2023-06-03 22:00:00",
                "i_commission_plan": None,
                "is_used": 0,
                "bill_status": "O",
                "name": customer_id,  # this is Site Name from CSV - Format: Customer_HQorRB_NAME_SAPCODE
                "login": siteName.replace("_", "") + "login_new",  # this is Site Name from CSV without _
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
                "companyname": siteName,  # Format: Customer_HQorRB_NAME_SAPCODE, same as site name
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

    t1_start = process_time()
    customer_response = requests.post(customer_api_url, json=customer_body, headers=headers, verify=False)
    t1_stop = process_time()
    turnaround_time = round((t1_stop - t1_start) * 1000)

    print(f'Create Customer:  response_code={customer_response.status_code}, turnaround_time: {turnaround_time}ms')
    print(customer_response.json())
    i_customer = customer_response.json()['i_customer']
    print(f'Customer ID:  i_customer={i_customer}')

    logger.info(f"Customer created, i_customer: {i_customer}")

    if officeType == 3:
        i_main_office = i_customer
    # endregion

    # Iterate through CSV customer file
    with open(csv_path + siteName + '.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        # Iteration loop starts here
        for row in csv_reader:
            # region Get info from CSV row
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1

            firstname = row["firstName"]
            lastname = row["lastName"]
            ext = row["extension"]
            ext_name = "ph" + str(i_customer) + "x" + ext
            did = row["phoneNumber"]

            cli = row["callingLineIdPhoneNumber"]
            if cli == "":
                cli = did

            product = row["servicePacks"]
            department = row["departmentName"]
            costCenter = row["yahooId"]
            email = row["userLinePorts[1]"]
            sip_account_password = uuid.uuid4()
            sip_account_password = str(sip_account_password)[:15]

            i_subscription = PROD_SUB_SETS[product][1]
            i_product = PROD_SUB_SETS[product][0]
            if i_product != 31025:
                prod_sub_count[i_product] += 1
            else:
                ext_name = input("Provide SIP trunk number: ")
            # endregion

            # region 2. Add SIP Account
            add_sip_account_api_url = "/Account/add_account"
            add_sip_account_headers = {"Authorization": f"Bearer {access_token}"}
            add_sip_account_body = {
                "params": {
                    "account_info": {
                        "billing_model": 1,
                        "email": email,
                        "h323_password": sip_account_password,
                        "i_customer": i_customer,
                        "i_product": i_product,  # 21322 onboarding product
                        "id": ext_name,  # this will be ph+icust+x+ext
                        "firstname": firstname,  # Firstname from CSV
                        "lastname": lastname  # Lastname from CSV
                    }
                }
            }

            print(f'Add Account Body: {add_sip_account_body}')

            t1_start = process_time()
            sip_account_response = requests.post(add_sip_account_api_url, json=add_sip_account_body,
                                                 headers=add_sip_account_headers, verify=False)
            t1_stop = process_time()
            turnaround_time = round((t1_stop - t1_start) * 1000)

            print(
                f'Create Account:  response_code={sip_account_response.status_code}, '
                f'turnaround_time: {turnaround_time}ms')
            print(sip_account_response.json())
            i_account = sip_account_response.json()['i_account']

            logger.info(f"SIP account created, i_account: {i_account}")

            # Add appropriate Subscription to SIP Account after its creation, based on account product.
            if i_subscription != 0:
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

                print(f'Add Subscription Body: {add_sip_account_body}')

                t1_start = process_time()
                response = requests.post(add_subscription_url, headers=add_subscription_header,
                                         json=add_subscription_body,
                                         verify=False)
                t1_stop = process_time()
                turnaround_time = round((t1_stop - t1_start) * 1000)

                print(
                    f'Added Subscription: response_code={response.status_code}, turnaround_time:'
                    f' {turnaround_time}ms')
                logger.info(f"Subscription added to {i_account}, i_subscription: {i_subscription}")

            # endregion

            # region Update custom field values
            get_schema_url = "/Account/update_custom_fields_values"
            get_schema_header = {"Authorization": f"Bearer {access_token}"}
            get_schema_body = {
                "params": {
                    "custom_fields_values": [
                        {
                            "db_value": costCenter,
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

            t1_start = process_time()
            response = requests.post(get_schema_url, headers=get_schema_header, json=get_schema_body, verify=False)
            t1_stop = process_time()
            turnaround_time = round((t1_stop - t1_start) * 1000)

            print(response.status_code)
            print(turnaround_time)

            logger.info(f"Customer variables have been added: Cost Center = {costCenter}, Department = {department}")
            # endregion

            # region 3. Create Cloud PABX Extension and Link with SIP Account
            add_customer_extension_api_url = "/Customer/add_customer_extension"
            add_customer_extension_headers = {"Authorization": f"Bearer {access_token}"}
            print(add_sip_account_headers)
            add_customer_extension_body = {
                "params": {
                    "i_account": i_account,  # this is the i_account variable written to the console on API add_account
                    "i_customer": i_customer,  # i_customer number retrieved from customer create api call
                    "id": ext,  # this is the extension number
                    "name": firstname + "." + lastname
                    # //this is Firstname.Lastname from CSV for extension name on cloudpbx
                }
            }

            i_c_ext = 0
            if ext:
                print(f'Add Account Body: {add_customer_extension_body}')

                t1_start = process_time()
                add_customer_extension_response = requests.post(add_customer_extension_api_url,
                                                                json=add_customer_extension_body,
                                                                headers=add_customer_extension_headers, verify=False)
                t1_stop = process_time()
                turnaround_time = round((t1_stop - t1_start) * 1000)

                print(
                    f'Add Customer Extension response:  response_code={add_customer_extension_response.status_code},'
                    f' turnaround_time: {turnaround_time}ms')
                print(add_customer_extension_response.json())
                i_c_ext = add_customer_extension_response.json()['i_c_ext']

                logger.info(f"Added Extension to i_customer {i_customer} and i_account {i_account}, i_c_ext: {i_c_ext}")
            # endregion

            # region store ph account id, name, and extension
            phAccountList.append([ext_name, str(i_account), ext])
            # endregion

            # region 4. Create and add to hunt group if receptionist
            if firstname == "Reception":
                if i_c_group == 0:
                    create_huntgroup_url = "/Customer/add_customer_huntgroup"
                    create_huntgroup_header = {"Authorization": f"Bearer {access_token}"}
                    create_huntgroup_body = {
                        "params": {
                            "activity_monitoring": "N",
                            "call_wrap_up_time": 0,
                            "hunt_keep_original_cli": "Y",
                            "hunt_sequence": "Simultaneous",
                            "hunt_while_wrapping_up": "always",
                            "i_customer": i_main_office,
                            "id": "99999",  # Get clarification about id for customers
                            "minimal_served_call_duration": 0,
                            "name": huntgroupName,  # Get customer hunt group name for receptionist
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
                    print(response.json())
                    i_c_group = response.json()['i_c_group']

                    print(response.status_code)
                    print(turnaround_time)

                    logger.info(f"Created Hunt group for Receptionists, i_c_group: {i_c_group}")

                # Add extension to hunt group
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
                        "i_c_group": i_c_group
                    }
                }

                print(f'Add Account Body: {add_customer_extension_body}')

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

                logger.info(f"Added i_account {i_account} i_c_ext {i_c_ext} to i_c_group {i_c_group}")
            # endregion

            # region Check whether there is a DID for this sip account and add to Porta, Customer, Account
            if did:
                # region Check which DID Group number belongs to
                i_group = 35
                for numRange in NUMBER_RANGES:
                    rangeIndex = did.find(numRange)
                    if rangeIndex == 0:
                        i_group = 24

                # endregion

                # region 5. Add DID to platform
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
                            "description": siteName,
                            # // i would like to have the Branchname as the description of the DID
                            #  IE Br_CapeTown_0800 from the csv
                            "number": did
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
                logger.info(f"Add DID to PortaOne platform, i_did_number: {i_did_number}")
                # endregion

                # region 6. Assign DID to customer
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
                print(assign_did_response.json())
                success = assign_did_response.json()['success']
                logger.info(f"Add DID to i_customer {i_customer}")
                # endregion

                # region 7. Assign DID to account
                add_account_did_url = "/DID/assign_did_to_account"
                add_account_did_header = {"Authorization": f"Bearer {access_token}"}
                add_account_did_body = {
                    "params": {
                        "i_did_number": i_did_number,  # The unique ID of the DID number record
                        "i_master_account": i_account  # The unique ID of the account this DID number is assigned to
                    }
                }

                print(f'Add DID to account Body: {add_account_did_body}')

                t1_start = process_time()
                add_account_did_response = requests.post(add_account_did_url,
                                                         json=add_account_did_body,
                                                         headers=add_account_did_header, verify=False)
                t1_stop = process_time()
                turnaround_time = round((t1_stop - t1_start) * 1000)
                logger.info(f"Add DID to i_master_account {i_account}")
                # endregion
            # endregion

            print('---------------------------------------------------------------')
            print(f'Site Name: {siteName}')
            print(f'Ext Name: {ext_name}')
            try:
                print(f'DID: {did} - Success Status={success}')
            except NameError:
                pass
            print('---------------------------------------------------------------')

            line_count += 1
        print(f'Processed {line_count} lines.')
        logger.info(f"Added {line_count} SIP accounts have been to i_customer {i_customer}")
        csv_file.close()

    # region Update Agreements
    update_agreement_info_url = "/Customer/update_agreement_conditions"
    update_agreement_info_header = {"Authorization": f"Bearer {access_token}"}
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
        t1_start = process_time()
        response = requests.post(update_agreement_info_url, headers=update_agreement_info_header,
                                 json=update_agreement_info_body, verify=False)
        t1_stop = process_time()
        turnaround_time = round((t1_stop - t1_start) * 1000)

        print(response.status_code)
        print(turnaround_time)

        logger.info(f"Updated agreements of i_customer {i_customer}")
    # endregion

    # region Store ph#####x#### account ID list in csv
    with open(csv_path + siteName + '_phAccount.csv', 'a', newline='') as phAccountCSV:
        csvWriter = csv.writer(phAccountCSV)
        csvWriter.writerow(['phName', 'phAccounts', 'extensions'])
        csvWriter.writerows(phAccountList)
        logger.info(f"Added sip accounts to csv file: {phAccountCSV.name}")
    # endregion

    # region Open pincode csv
    pincodeList: list[list[str]] = []
    try:
        with open(csv_path + siteName + '_Pincodes_Account.csv', 'r') as pincodeCSV:
            csv_reader = csv.DictReader(pincodeCSV)
            for row in csv_reader:
                row: dict
                pincodeList.append([row['pincode'], row['firstName'], row['lastName']])
            logger.info(f"Pincodes retrieved from csv file: {pincodeCSV.name}")

    except FileNotFoundError as e:
        logger.error(f"Pincode csv file was not found or does not exist")

    print(pincodeList)
    # endregion

    # region Get abbreviated numbers
    abbrivNumbersList: list[list[str]] = []
    try:
        with open(csv_path + siteName.split('_')[0] + '_Abbreviated_Number.csv', 'r') as abbrivNumberCSV:
            csv_reader = csv.DictReader(abbrivNumberCSV)
            for row in csv_reader:
                row: dict
                abbrivNumbersList.append([row['abbrNum'], row['numberToDial'], row['description']])
            logger.info(f"Abbreviated numbers retrieved from csv file: {abbrivNumberCSV.name}")

    except FileNotFoundError as e:
        logger.error(f"Abbreviated number csv file was not found or does not exist")

    print(abbrivNumbersList)
    # endregion

    # region Add pincode account into customer
    for pinAccount in pincodeList:
        firstName = pinAccount[1]
        lastName = pinAccount[2]
        pincodeID = "PIN_" + pinAccount[0] + "_" + firstName + "." + lastName
        sip_account_password = uuid.uuid4()
        sip_account_password = str(sip_account_password)[:15]

        add_sip_account_api_url = "/Account/add_account"
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

        print(
            f'Create Customer:  response_code={sip_account_response.status_code}, turnaround_time:'
            f' {turnaround_time}ms')
        print(sip_account_response.json())
        i_pincode_account = sip_account_response.json()['i_account']
        logger.info(f"PIN Account has been created, i_account: {i_pincode_account}")

        # region Add ph accounts to pincode account as aliases
        for phAccount in phAccountList:
            add_alias_url = "/rest/Account/add_alias"
            add_alias_header = {"Authorization": f"Bearer {access_token}"}
            add_alias_body = {
                "params": {
                    "alias_info": {
                        "i_master_account": i_pincode_account,
                        "i_account": int(phAccount[1]),
                        "id": f"{phAccount[0]}#{pinAccount[0]}"
                    }
                }
            }

            t1_start = process_time()
            response = requests.post(add_alias_url, headers=add_alias_header,
                                     json=add_alias_body, verify=False)
            t1_stop = process_time()
            turnaround_time = round((t1_stop - t1_start) * 1000)

            print(response.status_code)
            print(turnaround_time)

            logger.info(f"Account alias added to pincode {i_pincode_account}, aliased i_account: {i_account}")
        # endregion
    # endregion

    # region Add abbreviated dialing
    for abbrNum in abbrivNumbersList:
        add_abbr_number_url = "/rest/Customer/add_abbreviated_dialing_number"
        add_abbr_number_header = {"Authorization": f"Bearer {access_token}"}
        add_abbr_number_body = {
            "params": {
                "abbreviated_dialing_number_info": {
                    "abbreviated_number": abbrNum[0],
                    "description": abbrNum[2],
                    "number_to_dial": abbrNum[1]
                },
                "i_customer": i_customer
            }
        }

        t1_start = process_time()
        response = requests.post(add_abbr_number_url, headers=add_abbr_number_header, json=add_abbr_number_body,
                                 verify=False)
        t1_stop = process_time()
        turnaround_time = round((t1_stop - t1_start) * 1000)

        print(f"Status code: {response.status_code}")
        print(f"Turn around time: {turnaround_time}")

        logger.info(
            f"Abbreviated Number {abbrNum[0]} has been added to i_customer {i_customer}, number_to_dial: {abbrNum[1]}")
    # endregion

    print("Customer and accounts creation successful")
