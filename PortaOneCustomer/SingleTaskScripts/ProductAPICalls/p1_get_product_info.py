# Add subscription to account function. To be used in full customer import script
from time import process_time
import requests

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

get_product_url = "/rest/Product/get_product_info"
get_product_header = {"Authorization": f"Bearer {access_token}"}
get_product_body = {  # Check which other params are needed
    "params": {
        "i_product": 11649,  # Not working - 31025, working - 11649
    }
}

t1_start = process_time()
response = requests.post(get_product_url, headers=get_product_header, json=get_product_body,
                         verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

print(response.content)
