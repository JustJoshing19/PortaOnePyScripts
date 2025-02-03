from time import process_time
import requests

i_customer: int = 11229

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

add_abbr_number_url = "/Customer/add_abbreviated_dialing_number"
add_abbr_number_header = {"Authorization": f"Bearer {access_token}"}
add_abbr_number_body = {
    "params": {
        "abbreviated_dialing_number_info": {
            "abbreviated_number": "1111",
            "description": "string",
            "number_to_dial": "27999999999"
        },
        "i_customer": i_customer
    }
}

t1_start = process_time()
response = requests.post(add_abbr_number_url, headers=add_abbr_number_header, json=add_abbr_number_body,
                         verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(f"Status code: {response.status_code}")
print(f"Turn around time: {turnaround_time}")

print(f"{response.content}")
