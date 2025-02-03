import requests
from time import process_time

i_customer: int = 11229  # Test site to be used for testing API calls
i_account: int = 648283  # Test account whose info is requested. (To be changed when testing again)

if str.upper(input(f"Continue with the update of account {i_account}? (YES/NO): ")) != "YES":
    exit(0)

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

update_account_info_url = "/Account/update_account"
update_account_info_header = {"Authorization": f"Bearer {access_token}"}
update_account_info_body = {
    "params": {
        "account_info": {
            "i_account": i_account,
            "service_features": [{
                "attributes": [
                    {
                        "effective_values": [
                            "85D817%"
                        ],
                        "name": "outgoing_access_number",
                        "values": [
                            "85D817%"
                        ]
                    }
                ],
                "effective_flag_value": "Y",
                "flag_value": "Y",
                "locked": 0,
                "locks": [
                    "user"
                ],
                "name": "voice_pass_through"
            }]
        }
    }
}

t1_start = process_time()
response = requests.post(update_account_info_url, headers=update_account_info_header,
                         json=update_account_info_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

print(response.content)
