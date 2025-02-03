import requests
from time import process_time

i_customer: int = 15687
passw = input("password: ")

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

print(access_token)
print(expires_at)

# Make call to API to retrieve a list of accounts that belong to the given customer ID (i_customer)
list_accounts_url = "/Account/get_account_list"
list_accounts_header = {"Authorization": f"Bearer {access_token}"}
list_accounts_body = {
    "params": {
        "bill_status": "O",
        "i_customer": f"{i_customer}",
        "limit": 500,
        "offset": 0,
        "billing_model": 1,
        "id": "pin%"
    }
}
t1_start = process_time()
response = requests.post(list_accounts_url, headers=list_accounts_header, json=list_accounts_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(f"Status code: {response.status_code}")
print(f"Turn around time: {turnaround_time}")

print(f"Accounts on list: {response.json()}")

