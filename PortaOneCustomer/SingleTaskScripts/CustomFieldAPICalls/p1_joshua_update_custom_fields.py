import requests
from time import process_time

i_account: int = 614959

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

get_schema_url = "/Account/update_custom_fields_values"
get_schema_header = {"Authorization": f"Bearer {access_token}"}
get_schema_body = {
    "params": {
        "custom_fields_values": [
            {
                "db_value": "",
                "name": "Cost Center"
            },
            {
                "db_value": "",
                "name": "Department",
            }
        ],
        "i_account": i_account
    }
}

t1_start = process_time()
response = requests.post(get_schema_url, headers=get_schema_header, json=get_schema_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

print(response.content)
