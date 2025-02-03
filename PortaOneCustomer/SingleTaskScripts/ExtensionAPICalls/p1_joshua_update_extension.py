import requests
from time import process_time

i_customer: int = 10523
ext: str = "02365"

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

# Build request for Hunt group create API call
add_extension_url = "/rest/Customer/update_customer_extension"
add_extension_header = {"Authorization": f"Bearer {access_token}"}
add_extension_body = {
                "params": {
                    "id": ext,  # this is the extension number
                    "i_customer": i_customer,
                    "i_c_ext": 15632
                    # //this is Firstname.Lastname from CSV for extension name on cloudpbx
                }
            }

# Send request to create Hunt group
t1_start = process_time()
response = requests.post(add_extension_url, headers=add_extension_header,
                         json=add_extension_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

if response.status_code == 200:
    print("Extension was successfully updated.")
    print(response.content)
else:
    print("Error occurred:")
    print(response.content)
