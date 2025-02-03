import requests
from time import process_time

i_customer: int = 14980
i_group: int = 24

# Authenticate User and get session credentials to call other PortaOne API methods
login_api_url = "/Session/login"
passw = input("password: ")
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

add_did_api_url = "/DID/delete_number"
add_did_headers = {"Authorization": f"Bearer {access_token}"}
add_did_body = {
    "params": {
        "i_did_number": 1764938
    }
}

t1_start = process_time()
response = requests.post(add_did_api_url, headers=add_did_headers,
                         json=add_did_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

print(response.json())
