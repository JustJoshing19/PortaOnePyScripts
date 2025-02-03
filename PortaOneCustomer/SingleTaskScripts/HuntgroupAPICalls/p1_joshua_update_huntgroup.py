import requests
from time import process_time

i_customer: int = 14676
i_account: int = 616526
i_c_ext: int = 12418
i_c_group: int = 1303

# Authenticate User and get session credentials to call other PortaOne API methods
login_api_url = "/rest/Session/login"
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

# Build request for Hunt group create API call
update_huntgroup_url = "/rest/Customer/update_customer_huntgroup"
update_huntgroup_header = {"Authorization": f"Bearer {access_token}"}
update_huntgroup_body = {
    "params": {
        "add_extensions": [
            {
                "account_id": i_account,
                "i_c_ext": i_c_ext
            }
        ],
        "i_c_group": i_c_group
    }
}

# Send request to create Hunt group
t1_start = process_time()
response = requests.post(update_huntgroup_url, headers=update_huntgroup_header,
                         json=update_huntgroup_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

if response.status_code == 200:
    print("Hunt group was successfully added.")
else:
    print("Error occurred:")

print(response.content)
