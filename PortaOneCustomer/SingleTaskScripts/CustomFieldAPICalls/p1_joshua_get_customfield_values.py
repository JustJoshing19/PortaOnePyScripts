import requests
from time import process_time

i_account: int = 655579
passw = input("password: ")
# PIN code Account with custom fields

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

get_values_url = "/Account/get_custom_fields_values"
get_values_header = {"Authorization": f"Bearer {access_token}"}
get_values_body = {
    "params": {
        "i_account": i_account  # i_account for PIN_950420_Chris.Terblanche
    }
}

t1_start = process_time()
response = requests.post(get_values_url, headers=get_values_header, json=get_values_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

print(response.content)
