import csv
from tkinter import filedialog

phonebook_num_list: list[dict] = []
with open(filedialog.askopenfilename(), "r") as file:
    csv_file = csv.DictReader(file)
    for number in csv_file:
        number: dict
        pbk_entry = {
            "ct_displayName": number["display_name"],
            "ct_officeNumber": number["office_number"],
            "ct_mobileNumber": None,
            "ct_line": "0",
            "ct_groupName": "All Contacts"
        }
        phonebook_num_list.append(pbk_entry)

customer = int(input("Customer id: "))
pkb_file_name = input("Phonebook's filename: ")

post_pkb_body = {
    "pbk_groups": [
        {
            "gp_displayName": "All Contacts"
        },
        {
            "gp_displayName": "Blacklist"
        }
    ],
    "pbk_contacts": phonebook_num_list,
    "instance": "",
    "i_customer": customer,
    "pbk_filename": pkb_file_name
}

print(post_pkb_body)
