import requests
from time import process_time

i_customer: int = 14912  # Test site to be used for testing API calls
i_c_ext: int = 11975  # Extension to be removed

if str.upper(input("Continue with delete function? (YES/NO): ")) != "YES":
    exit(0)

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

remove_extension_url = "/rest/Customer/delete_customer_extension"
remove_extension_header = {"Authorization": f"Bearer {access_token}"}
remove_extension_body = {
    "params": {
        "dont_release_did_number_to_pool": 1,
        "i_c_ext": i_c_ext,
        "i_customer": i_customer
    }
}

t1_start = process_time()
response = requests.post(remove_extension_url, headers=remove_extension_header,
                         json=remove_extension_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)
