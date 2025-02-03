import requests
from time import process_time

i_account: int = 614959  # Test account to be deleted. (To be changed when running script again)

if str.upper(input(f"Continue with the termination of account {i_account}? (YES/NO): ")) != "YES":
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
