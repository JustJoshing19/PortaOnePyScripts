import requests
from time import process_time

i_account: int = 643909  # Extension ID
i_did_account: int = 1762324

# Authenticate User and get session credentials to call other PortaOne API methods
login_api_url = "/Session/login"
passw1 = input("password: ")
login_body = {'params': {'login': 'joshuar', 'password': passw1}}

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

add_did_url = "/DID/assign_did_to_account"
add_did_header = {"Authorization": f"Bearer {access_token}"}
add_did_body = {
    "params": {
        "i_did_number": i_did_account,  # The unique ID of the DID number record
        "i_master_account": i_account  # The unique ID of the account this DID number is assigned to
    }
}

t1_start = process_time()
response = requests.post(add_did_url, headers=add_did_header, json=add_did_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

print(response.content)
