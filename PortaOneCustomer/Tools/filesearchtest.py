import csv
import sys

from tkinter import filedialog

filePath = filedialog.askopenfilename()
line_count = 0

with open(filePath, 'r', newline='') as phAccountCSV:
    csvDictReader = csv.DictReader(phAccountCSV)
    for row in csvDictReader:
        row: dict
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        print(row)
