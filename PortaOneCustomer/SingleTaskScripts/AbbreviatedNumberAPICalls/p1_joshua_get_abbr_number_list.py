# To be implemented to full import script.
from time import process_time
import requests

i_customer: int = 18688

# Authenticate User and get session credentials to call other PortaOne API methods
login_api_url = "/Session/login"

password = input("Password: ")
login_body = {'params': {'login': 'joshuar', 'password': password}}

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

list_abbr_number_url = "/Customer/get_abbreviated_dialing_number_list"
list_abbr_number_header = {"Authorization": f"Bearer {access_token}"}
list_abbr_number_body = {
    "params": {
        "i_customer": i_customer,
        "limit": 300,
        "offset": 0
    }
}

t1_start = process_time()
response = requests.post(list_abbr_number_url, headers=list_abbr_number_header, json=list_abbr_number_body,
                         verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(f"Status code: {response.status_code}")
print(f"Turn around time: {turnaround_time}")

print(f"Full List: {response.content}")
