import requests
from time import process_time
import uuid

i_account: int = 617677  # Test site to be used for testing

# Authenticate User and get session credentials to call other PortaOne API methods
login_api_url = "/Session/login"
passw = input("Password: ")
login_body = {'params': {'login': 'joshuar', 'password': passw}}

t1_start = process_time()
response = requests.post(login_api_url, json=login_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

access_token = response.json()['access_token']  # Store access token for future API calls
expires_at = response.json()['expires_at']  # Store access token expiry date for if refresh is needed

# Build request for create account API call
create_account_url = "/Account/get_subscriptions"
create_account_header = {"Authorization": f"Bearer {access_token}"}
create_account_body = {
    "params": {
        "i_account": i_account
    }
}

# Send request to create account
t1_start = process_time()
response = requests.post(create_account_url, headers=create_account_header,
                         json=create_account_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

if response.status_code == 200:
    print("Account was successfully added.")
else:
    print("Error occurred:")

print(response.content)
