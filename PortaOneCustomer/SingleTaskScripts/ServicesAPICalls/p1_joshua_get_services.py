# Add subscription to account function. To be used in full customer import script
from time import process_time
import requests

# Authenticate User and get session credentials to call other PortaOne API methods
passw = input("Password: ")

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

get_product_url = "/Service/get_service_list"
get_product_header = {"Authorization": f"Bearer {access_token}"}
get_product_body = {  # Check which other params are needed
    "params": {
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
