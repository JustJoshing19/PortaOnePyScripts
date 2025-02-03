import requests
from time import process_time

# Authenticate User and get session credentials to call other PortaOne API methods
login_api_url = "/rest/Session/login"
passw = input("password: ")
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

get_subscription_url = "/rest/Subscription/get_subscription_info"
get_subscription_header = {"Authorization": f"Bearer {access_token}"}
get_subscription_body = {
    "params": {
        "i_subscription": 18086
    }
}

t1_start = process_time()
response = requests.post(get_subscription_url, headers=get_subscription_header, json=get_subscription_body,
                         verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

print(response.content)
