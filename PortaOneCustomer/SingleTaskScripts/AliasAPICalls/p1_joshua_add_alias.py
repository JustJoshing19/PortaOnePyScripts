import requests
from time import process_time

i_account: int = 549150  # Test account whose info is requested. (To be changed when testing again)

# Authenticate User and get session credentials to call other PortaOne API methods
login_api_url = "/Session/login"
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

add_alias_url = "/Account/add_alias"
add_alias_header = {"Authorization": f"Bearer {access_token}"}
add_alias_body = {
  "params": {
    "alias_info": {
      "i_master_account": 1,
      "id": "alias-id@somewhere.com"
    }
  }
}

t1_start = process_time()
response = requests.post(add_alias_url, headers=add_alias_header,
                         json=add_alias_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

print(response.content)
