import csv
from tkinter import filedialog

file_path = filedialog.askopenfilename()

abbr_list: list[dict] = []
with open(file_path, 'r') as abbr_csv:
    dict_reader = csv.DictReader(abbr_csv)
    for row in dict_reader:
        row: dict
        abbr_list.append(row)

for i in range(0, len(abbr_list)):
    abbr_list[i]["numberToDial"] = "27" + abbr_list[i]["numberToDial"]

print(abbr_list)
new_file_path = file_path[:-4] + '_Formatted' + file_path[-4:]
with open(new_file_path, 'w', newline='') as abbr_csv:
    dict_writer = csv.DictWriter(abbr_csv, ['abbrNum', 'description', 'numberToDial'])
    dict_writer.writeheader()
    dict_writer.writerows(abbr_list)
