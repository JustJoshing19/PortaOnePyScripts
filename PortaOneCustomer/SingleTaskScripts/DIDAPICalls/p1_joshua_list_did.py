import requests
from time import process_time

i_customer: int = 11229

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

print(access_token)
print(expires_at)

list_did_url = "/DID/get_number_list"
list_did_header = {"Authorization": f"Bearer {access_token}"}
list_did_body = {
    "params": {
        "i_customer": i_customer
    }
}

t1_start = process_time()
response = requests.post(list_did_url, headers=list_did_header, json=list_did_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

print(response.content)
