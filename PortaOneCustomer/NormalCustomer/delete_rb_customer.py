import requests
from time import process_time

ph_accounts_list: list = []
extension_list: list = []
did_list: list = []

hq_i_customer = int(input("HQ id: "))
rb_i_customer = int(input("RB id: "))

passw = input("password: ")

if str.upper(input(f"Continue with the termination of accounts on {rb_i_customer}? (YES/NO): ")) != "YES":
    exit(0)

# Authenticate User and get session credentials to call other PortaOne API methods
login_api_url = "/Session/login"
login_body = {'params': {'login': 'joshuar', 'password': passw}}

t1_start = process_time()
response = requests.post(login_api_url, json=login_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

access_token = response.json()['access_token']  # Store access token for future API calls
expires_at = response.json()['expires_at']  # Store access token expiry date for if refresh is needed

# region did list
list_did_url = "/DID/get_number_list"
list_did_header = {"Authorization": f"Bearer {access_token}"}
list_did_body = {
    "params": {
        "i_customer": rb_i_customer
    }
}

t1_start = process_time()
response = requests.post(list_did_url, headers=list_did_header, json=list_did_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

print(response.content)

for did in response.json()['number_list']:
    print(did['i_did_number'])
    did_list.append(did['i_did_number'])

print(did_list)
# endregion

# region get extension list
get_extension_list_url = "/Customer/get_extensions_list"
get_extension_list_header = {"Authorization": f"Bearer {access_token}"}
get_extension_list_body = {
    "params": {
        "i_customer": hq_i_customer
    }
}

t1_start = process_time()
response = requests.post(get_extension_list_url, headers=get_extension_list_header,
                         json=get_extension_list_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

print(response.content)

for ext in response.json()['extensions_list']:
    if ext['i_customer_of_account'] == rb_i_customer:
        print(ext['i_c_ext'])
        extension_list.append(ext['i_c_ext'])

print(extension_list)
# endregion

# region delete extensions
for ext in extension_list:
    remove_extension_url = "/Customer/delete_customer_extension"
    remove_extension_header = {"Authorization": f"Bearer {access_token}"}
    remove_extension_body = {
        "params": {
            "dont_release_did_number_to_pool": 1,
            "i_c_ext": ext,
            "i_customer": hq_i_customer
        }
    }

    t1_start = process_time()
    response = requests.post(remove_extension_url, headers=remove_extension_header,
                             json=remove_extension_body, verify=False)
    t1_stop = process_time()
    turnaround_time = round((t1_stop - t1_start) * 1000)

    print(response.status_code)
    print(turnaround_time)
# endregion

# region get account list
list_accounts_url = "/Account/get_account_list"
list_accounts_header = {"Authorization": f"Bearer {access_token}"}
list_accounts_body = {
            "params": {
                "bill_status": "O",
                "i_customer": f"{rb_i_customer}",
                "billing_model": 1,
                "id": "ph%",
                "limit": 200,
                "offset": 0
            }
        }
t1_start = process_time()
response = requests.post(list_accounts_url, headers=list_accounts_header, json=list_accounts_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(f"Status code: {response.status_code}")
print(f"Turn around time: {turnaround_time}")

print(f"Full List: {response.content}")

for acc in response.json()['account_list']:
    print(acc['id'])
    ph_accounts_list.append(acc['i_account'])

print(ph_accounts_list)
# endregion

# region delete accounts
for i_account in ph_accounts_list:
    delete_account_url = "/Account/terminate_account"
    delete_account_header = {"Authorization": f"Bearer {access_token}"}
    delete_account_body = {
        "params": {
            "i_account": i_account  # Number of account that is going to be deleted.
        }
    }

    t1_start = process_time()
    response = requests.post(delete_account_url, headers=delete_account_header, json=delete_account_body, verify=False)
    t1_stop = process_time()
    turnaround_time = round((t1_stop - t1_start) * 1000)

    print(response.status_code)
    print(turnaround_time)

    print(response.content)
# endregion


# region terminate customer
terminate_customer_url = "/Customer/terminate_customer"
terminate_customer_header = {"Authorization": f"Bearer {access_token}"}
terminate_customer_body = {
    "params": {
        "i_customer": rb_i_customer,
        "supress_notification": 0
    }
}

t1_start = process_time()
response = requests.post(terminate_customer_url, headers=terminate_customer_header, json=terminate_customer_body,
                         verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

print(response.content)
# endregion

# region delete DIDs
for did in did_list:
    release_did_url = "/DID/release_did_from_customer"
    release_did_header = {"Authorization": f"Bearer {access_token}"}
    release_did_body = {
        "params": {
            "i_did_number": did
        }
    }

    t1_start = process_time()
    response = requests.post(release_did_url, headers=release_did_header, json=release_did_body, verify=False)
    t1_stop = process_time()
    turnaround_time = round((t1_stop - t1_start) * 1000)

    print(response.status_code)
    print(turnaround_time)

    print(response.content)

    delete_did_url = "/DID/delete_number"
    delete_did_header = {"Authorization": f"Bearer {access_token}"}
    delete_did_body = {
        "params": {
            "i_did_number": did
        }
    }

    t1_start = process_time()
    response = requests.post(delete_did_url, headers=delete_did_header, json=delete_did_body, verify=False)
    t1_stop = process_time()
    turnaround_time = round((t1_stop - t1_start) * 1000)

    print(response.status_code)
    print(turnaround_time)

    print(response.content)
# endregion
