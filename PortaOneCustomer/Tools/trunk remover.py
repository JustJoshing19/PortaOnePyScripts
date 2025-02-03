import csv

from tkinter import filedialog

trunk_file = filedialog.askopenfilename()

trunk_account_numbers: list[str] = []
with open(trunk_file, 'r') as t_file:
    csv_reader = csv.DictReader(t_file)
    for row in csv_reader:
        row: dict
        row['callingLineIdPhoneNumber'] = "27" + row['callingLineIdPhoneNumber'][1:]
        trunk_account_numbers.append(row['callingLineIdPhoneNumber'])

pin_account_file = filedialog.askopenfilename()

pin_acccounts: list = []
with open(pin_account_file, 'r') as p_file:
    csv_reader = csv.DictReader(p_file)
    for row in csv_reader:
        row: dict
        pin_acccounts.append(row)

edited_account_list = pin_acccounts.copy()

match_count = 0
for account in pin_acccounts:

    phoneNumber = account['callingLineIdPhoneNumber']
    if phoneNumber in trunk_account_numbers:
        print(phoneNumber + " " + trunk_account_numbers[trunk_account_numbers.index(phoneNumber)])
        match_count += 1

        edited_account_list.pop(edited_account_list.index(account))

    else:
        print(phoneNumber)

pin_account_file = pin_account_file[pin_account_file.rfind('/') + 1:]
with open('edited_' + pin_account_file, 'a', newline='') as e_file:
    csv_wrtier = csv.writer(e_file)
    csv_wrtier.writerow(['groupId', 'lastName', 'firstName', 'callingLineIdPhoneNumber', 'extension',
                         'accessDeviceEndpoint.accessDevice.macAddress', 'yahooId', 'phoneNumber',
                         'servicePacks', 'trunkAddressing.alternateTrunkIdentity', 'impId'])
    for row in edited_account_list:
        row: dict
        data = list(row.values())
        csv_wrtier.writerow(data)

print("Matches: " + str(match_count))
print("Length of non trunk account list: " + str(len(edited_account_list)))
