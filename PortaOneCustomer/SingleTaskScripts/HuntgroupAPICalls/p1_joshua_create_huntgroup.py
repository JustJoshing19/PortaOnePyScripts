import requests
from time import process_time

i_customer: int = 11229

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

# Build request for Hunt group create API call
create_huntgroup_url = "/rest/Customer/add_customer_huntgroup"
create_huntgroup_header = {"Authorization": f"Bearer {access_token}"}
create_huntgroup_body = {
    "params": {
        "activity_monitoring": "N",
        "call_wrap_up_time": 0,
        "hunt_keep_original_cli": "Y",
        "hunt_sequence": "Simultaneous",
        "hunt_while_wrapping_up": "always",
        "i_customer": i_customer,
        "id": "99999",
        "minimal_served_call_duration": 0,
        "name": "HG_zzzAPI_Joshua",
        "pickup_allowed": "Y",
        "wrap_up_extend_time": 0,
        "wrap_up_passed_calls": "N"
    }
}

# Send request to create Hunt group
t1_start = process_time()
response = requests.post(create_huntgroup_url, headers=create_huntgroup_header,
                         json=create_huntgroup_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

if response.status_code == 200:
    print("Hunt group was successfully added.")
else:
    print("Error occurred:")
    print(response.content)
