import requests
from time import process_time

i_customer: int = 11229  # Test site to be used for testing API calls
i_account: int = 611239  # Test account whose info is requested. (To be changed when testing again)

if str.upper(input(f"Continue with the moving of account {i_account}? (YES/NO): ")) != "YES":
    exit(0)

# Authenticate User and get session credentials to call other PortaOne API methods
login_api_url = "/Session/login"
login_body = {'params': {'login': 'joshuar', 'token': ''}}

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

move_account_info_url = "/Account/move_account"
move_account_info_header = {"Authorization": f"Bearer {access_token}"}
move_account_info_body = {
  "params": {
    "batch_name": "string",
    "i_account": 1,
    "i_customer": 1,
    "i_product": 1,
    "i_routing_plan": 1,
    "i_vd_plan": 1
  }
}

t1_start = process_time()
response = requests.post(move_account_info_url, headers=move_account_info_header,
                         json=move_account_info_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

print(response.content)
