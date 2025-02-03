import requests
from time import process_time

i_customer: int = 11229

# Authenticate User and get session credentials to call other PortaOne API methods
login_api_url = "/rest/Session/login"
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

list_accounts_url = "/rest/Tariff/rerate_xdrs"
list_accounts_header = {"Authorization": f"Bearer {access_token}"}
list_accounts_body = {
    "params": {
        "date_from": "2000-01-01 08:00:00",
        "date_to": "2000-01-01 08:00:00",
        "effective_time": "2000-01-01 08:00:00",
        "i_owner": i_customer,
        "i_service": 1,
        "i_tariff_correct": 1,
        "i_tariff_wrong": 1,
        "owner": "string",
        "process_imported_charges": 1,
        "use_override_tariffs": "string"
    }
}

t1_start = process_time()
response = requests.post(list_accounts_url, headers=list_accounts_header, json=list_accounts_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(f"Status code: {response.status_code}")
print(f"Turn around time: {turnaround_time}")

print(f"{response.content}")
