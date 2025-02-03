import requests
from time import process_time

i_customer: int = 14984
i_account: int = 789382
ext: int = 5246
firstname = "Martin"
lastname = "Louw"

# Authenticate User and get session credentials to call other PortaOne API methods
login_api_url = "/Session/login"
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
add_extension_url = "/Customer/add_customer_extension"
add_extension_header = {"Authorization": f"Bearer {access_token}"}
add_extension_body = {
                "params": {
                    "i_account": i_account,  # this is the i_account variable written to the console on API add_account
                    "i_customer": i_customer,  # i_customer number retrieved from customer create api call
                    "id": ext,  # this is the extension number
                    "name": firstname + "." + lastname
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
    print("Extension was successfully created.")
    print(response.content)
else:
    print("Error occurred:")
    print(response.content)
