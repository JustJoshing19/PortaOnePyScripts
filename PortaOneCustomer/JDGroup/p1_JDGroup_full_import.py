# Full customer import for JDGroup or similar customer
import requests
import csv
import uuid

from time import process_time
from tkinter import filedialog

# Contains the product/subscription combination for each main product
PROD_SUB_SETS = {"JDGBASIC": [15854, 0],
                 "AUTOATTENDANT": [14409, 0]}  # Different product sets for normal customer JDGroup, And Clini. get
# JDGroup Product set from Chris when done

# region Get file path and name
file_path = filedialog.askopenfilename()

slashIndex: int = file_path.rfind('/') + 1

siteName = file_path[slashIndex:-4]
csv_path = file_path[:slashIndex]

huntgroupName = "HG_" + siteName
# endregion
i_AA_account: int = 0

# region Get credit limit from user
credit_limit = -1  # Set the site Credit limit here
while credit_limit < 0:
    try:
        limit = int(input("Please enter credit limit: "))
        if str.upper(input(f"Proceed with a credit limit {limit} (yes/no)")) == "YES":
            credit_limit: int = limit
            print(f"Credit limit is {credit_limit}")
    except ValueError as e:
        print("Please enter a valid limit, digits only")
# endregion

# region Get Display Number for Group
Main_Number = ""
with open(csv_path + siteName + '.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        row: dict
        if row["extension"].find('0', -1) != -1:
            Main_Number: str = row["callingLineIdPhoneNumber"]
            Main_Number.replace('0', '27', 1)
# endregion

# All JD Group customers will be main offices
officeType = 3  # 3 - main_office

# region Log in & get access_token
login_api_url = ""
login_body = {'params': {'login': '', 'token': ''}}
t1_start = process_time()
response = requests.post(login_api_url, json=login_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
# endregion

if response.status_code == 200:
    access_token = response.json()['access_token']
    expires_at = response.json()['expires_at']
    print(f'Login Successful! expires_at: {expires_at}, turnaround_time: {turnaround_time}ms')

    customer_cloudPBX_Password = uuid.uuid4()
    customer_cloudPBX_Password = str(customer_cloudPBX_Password)[:15]

    # region 1. Create customer - currently not specifying branch/HQ info
    headers = {"Authorization": f"Bearer {access_token}"}
    customer_api_url = "/Customer/add_customer"
    customer_body = {
        "params": {
            "customer_info": {
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
                "name": siteName,  # this is Site Name from CSV - Format: Customer_HQorRB_NAME_SAPCODE
                "login": siteName.replace("_", "") + "login",  # this is Site Name from CSV without _
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
                                    Main_Number
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
    # endregion

    # region 2. Create Hunt Group for JD Group customer
    # Check what other params are required.
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
            "id": "99999",
            "minimal_served_call_duration": 0,
            "name": huntgroupName,
            "pickup_allowed": "Y",
            "wrap_up_extend_time": 0,
            "wrap_up_passed_calls": "N"
        }
    }

    t1_start = process_time()
    huntgroup_response = requests.post(create_huntgroup_url, json=create_huntgroup_body,
                                       headers=create_huntgroup_header,
                                       verify=False)
    t1_stop = process_time()
    turnaround_time = round((t1_stop - t1_start) * 1000)

    print(f'Create Hunt Group:  response_code={huntgroup_response.status_code}, turnaround_time: {turnaround_time}ms')
    print(huntgroup_response.json())
    i_c_group = huntgroup_response.json()['i_c_group']
    print(f'Hunt Group ID:  i_c_group={i_c_group}')
    # endregion

    # region Add Auto Attendant
    sip_account_password = uuid.uuid4()
    sip_account_password = str(sip_account_password)[:15]
    add_sip_account_api_url = "/Account/add_account"
    add_sip_account_headers = {"Authorization": f"Bearer {access_token}"}
    print(add_sip_account_headers)
    add_sip_account_body = {
        "params": {
            "account_info": {
                "billing_model": 1,
                "h323_password": sip_account_password,
                "i_customer": i_customer,
                "i_product": 14409,
                "id": Main_Number,  # The main number aof the Auto Attendant
                "firstname": siteName,  # Site of Auto Attendant
                "lastname": "Auto Attendant"
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
    i_AA_account = sip_account_response.json()['i_account']
    # endregion

    # Open CSV
    with open(csv_path + siteName + '.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        # Iterate through CSV customer file
        # Iteration loop starts here
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            print(
                f'{row["Lastname"]}, {row["Firstname"]}, {row["Ext"]}, {row["DID"]}, {row["DID description"]},'
                f' {row["i_product"]}')

            firstname = row["Firstname"]
            lastname = row["Lastname"]
            ext = row["Ext"]
            ext_name = "ph" + i_customer + "x" + ext
            did = row["DID"]
            did_description = row["DID description"]
            i_product = row["i_product"]
            sip_account_password = uuid.uuid4()
            sip_account_password = str(sip_account_password)[:15]

            i_product = PROD_SUB_SETS[i_product][0]
            i_subscription = PROD_SUB_SETS[i_product][1]

            # region 3. Add SIP Account
            add_sip_account_api_url = "/Account/add_account"
            add_sip_account_headers = {"Authorization": f"Bearer {access_token}"}
            print(add_sip_account_headers)
            add_sip_account_body = {
                "params": {
                    "account_info": {
                        "billing_model": 1,
                        "h323_password": sip_account_password,
                        "i_customer": i_customer,
                        "i_product": i_product,
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
                f'Create Customer:  response_code={sip_account_response.status_code}, turnaround_time:'
                f' {turnaround_time}ms')
            print(sip_account_response.json())
            i_account = sip_account_response.json()['i_account']

            # Add Subscription to SIP Account after its creation, based on account product.
            if i_subscription != 0:
                add_subscription_url = "/Account/add_subscription"
                add_subscription_header = {"Authorization": f"Bearer {access_token}"}
                add_subscription_body = {  # Check which other params are needed
                    "params": {
                        "i_account": 1,
                        "subscription_info": {
                            "i_account": 1,
                            "i_product": 1,
                            "i_subscription": 1
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
            # endregion

            # region 4. Create Cloud PABX Extension and Link with SIP Account
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

            print(f'Create Extension Body: {add_customer_extension_body}')

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
            # endregion

            # region 5. Add extension to hunt group
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
            update_huntgroup_response = requests.post(add_customer_extension_api_url,
                                                      json=add_customer_extension_body,
                                                      headers=add_customer_extension_headers, verify=False)
            t1_stop = process_time()
            turnaround_time = round((t1_stop - t1_start) * 1000)

            print(
                f'Add Extension to Hunt Group response:  response_code={update_huntgroup_response.status_code},'
                f' turnaround_time: {turnaround_time}ms')
            print(update_huntgroup_response.json())
            i_c_ext = update_huntgroup_response.json()['i_c_ext']
            # endregion

            print('---------------------------------------------------------------')
            print(f'Site Name: {siteName}')
            print(f'Ext Name: {ext_name}')
            print(f'DID: {did} - Success Status=""')
            print('---------------------------------------------------------------')

            line_count += 1
        print(f'Processed {line_count} lines.')
        csv_file.close()
