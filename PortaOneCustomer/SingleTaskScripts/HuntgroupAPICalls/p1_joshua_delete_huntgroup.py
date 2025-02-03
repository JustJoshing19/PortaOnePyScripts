import requests
from time import process_time

i_customer: int = 11229  # Test site to be used for testing API calls

if str.upper(input("Continue with delete function? (YES/NO): ")) != "YES":
    exit(0)

i_c_group: int = int(input("Please enter id of hunt group to delete: "))

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

get_huntgroup_info_url = "/rest/Customer/delete_customer_huntgroup"
get_huntgroup_info_header = {"Authorization": f"Bearer {access_token}"}
get_huntgroup_info_body = {
    "params": {
        "i_c_group": i_c_group
    }
}

t1_start = process_time()
response = requests.post(get_huntgroup_info_url, headers=get_huntgroup_info_header,
                         json=get_huntgroup_info_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

print(response.content)
