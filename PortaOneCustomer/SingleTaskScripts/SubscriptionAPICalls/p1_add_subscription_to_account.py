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

add_subscription_url = "/rest/Account/add_subscription"
add_subscription_header = {"Authorization": f"Bearer {access_token}"}
add_subscription_body = {  # Check which other params are needed
    "params": {
        "i_account": 1,
        "subscription_info": {
            "i_account": 1,
            "i_product": 1,
            "i_subscription": 1
        }
    }
}

t1_start = process_time()
response = requests.post(add_subscription_url, headers=add_subscription_header, json=add_subscription_body,
                         verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

print(response.content)
