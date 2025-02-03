import requests
from time import process_time

i_customer: int = 14980
i_group: int = 24

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

add_did_api_url = "/DID/add_number"
add_did_headers = {"Authorization": f"Bearer {access_token}"}
add_did_body = {
    "params": {
        "number_info": {
            "activation_cost": 0.0,
            "activation_fee": 0.0,
            "activation_revenue": 0.0,
            "country_iso": "ZA",
            "country_name": "South Africa",
            "periodic_fee": 0.0,
            "recurring_cost": 0.0,
            "vendor_batch_name": "Gijima SBC Test",
            "external": 1,
            "free_of_charge": "N",
            "i_dv_batch": 114,
            "i_do_batch": 147,
            "i_group": i_group,
            "i_vendor": 152,
            "is_used": 1,
            "iso_4217": "ZAR",
            "frozen": "N",
            # //variables apply to the below
            "description": 'TWINSAVER_HQ_Bryanston_0000',
            # // i would like to have the Branchname as the description of the DID
            #  IE Br_CapeTown_0800 from the csv
            "number": 27101331152  # //this is the actual DID number is 164 format I want to variable this from CSV
        }
    }
}

t1_start = process_time()
response = requests.post(add_did_api_url, headers=add_did_headers,
                         json=add_did_body, verify=False)
t1_stop = process_time()
turnaround_time = round((t1_stop - t1_start) * 1000)

print(response.status_code)
print(turnaround_time)

print(response.json())
