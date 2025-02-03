from time import process_time
import requests

i_ab_dialing: int = 0

if str.upper(input(f"Continue with the termination of abbreviated number {i_ab_dialing}? (YES/NO): ")) != "YES":
    exit(0)

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

delete_abbr_number_url = "/Customer/delete_abbreviated_dialing_number"
delete_abbr_number_header = {"Authorization": f"Bearer {access_token}"}
delete_abbr_number_body = {
    "params": {
        "i_ab_dialing": 1
    }
}

t1_start = process_time()
response = requests.post(delete_abbr_number_url, headers=delete_abbr_number_header,
                         json=delete_abbr_number_body,
                         verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(f"Status code: {response.status_code}")
print(f"Turn around time: {turnaround_time}")

print(f"{response.content}")
