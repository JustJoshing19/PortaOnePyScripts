import json
import logging
import re
import sys
from datetime import datetime
from getpass import getpass

import requests
import csv
import uuid

from time import process_time
from tkinter import filedialog

import xml.etree.ElementTree as ET

pbk_list: list[dict] = []

with open(filedialog.askopenfilename(), "r") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for entry in csv_reader:
        entry: dict
        pbk_list.append(entry)

root: ET.Element = ET.Element('YealinkIPPhoneDirectory')
for entry in pbk_list:
    dirEnt = ET.Element("DirectoryEntry ")

    dName = entry["display_name"]
    eName = ET.Element("Name")
    eName.text = dName

    id_num = entry["id"]
    eNumber = ET.Element("Telephone")
    eNumber.text = id_num

    dirEnt.append(eName)
    dirEnt.append(eNumber)
    root.append(dirEnt)


print(ET.tostring(root))
