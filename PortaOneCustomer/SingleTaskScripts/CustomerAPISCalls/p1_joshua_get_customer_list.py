import requests
from time import process_time
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

get_account_info_url = "/Customer/get_customer_list"
get_account_info_header = {"Authorization": f"Bearer {access_token}"}
get_account_info_body = {
    "params": {
        "offset": 0,
        "limit": 500
    }
}

t1_start = process_time()
response = requests.post(get_account_info_url, headers=get_account_info_header,
                         json=get_account_info_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

print(response.content)
