import requests
from time import process_time

i_customer: int = 15262  # Test account whose info is requested. (To be changed when testing again)
passw = input("Password: ")
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

update_customer_info_url = "/Customer/update_customer"
update_customer_info_header = {"Authorization": f"Bearer {access_token}"}
update_customer_info_body = {
    "params": {
        "customer_info": {
            "i_customer": i_customer,
            "max_abbreviated_length": 5
        }
    }}

t1_start = process_time()
response = requests.post(update_customer_info_url, headers=update_customer_info_header,
                         json=update_customer_info_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

print(response.content)
