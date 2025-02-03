import csv

from tkinter import filedialog


def get_csv_data(file_path: str) -> list[list[str]]:
    data: list[list[str]] = []
    with open(file_path, 'r') as odin_file:
        reader = csv.DictReader(odin_file)
        for row in reader:
            row: dict
            row_data = []
            if ("ï»¿Code" in row.keys()) and (row["ï»¿Code"] is not None):
                row_data.append(row["ï»¿Code"])
                row_data.append(row["Description"])
                data.append(row_data)
            elif ("Code" in row.keys()) and (row["Code"] is not None):
                row_data.append(row["ï»¿Code"])
                row_data.append(row["Description"])
                data.append(row_data)
            elif ('ï»¿"Code"' in row.keys()) and (row['ï»¿"Code"'] is not None):
                row_data.append(row['ï»¿"Code"'])
                row_data.append(row["Description"])
                data.append(row_data)

    return data


def split_names(data: list[list[str]]) -> list[list[str]]:
    for row in data:
        first_last_name = row.pop(1).split(" ")
        row.append(first_last_name[0])

        last_name = first_last_name[1]
        for part in first_last_name[2:]:
            last_name = last_name + '.' + part
        row.append(last_name)

    return data


def create_csv_file(file_name, data: list[list[str]]) -> bool:
    try:
        with open(file_name, 'a', newline='') as formatted_file:
            csv_writer = csv.writer(formatted_file)
            csv_writer.writerow(['pincode', 'firstName', 'lastName'])
            csv_writer.writerows(data)
    except ValueError:
        return False

    return True


def get_site_name(file_path: str) -> str:
    name_begin = file_path.rfind("/")
    file_name = file_path[name_begin + 1:]
    site = file_name.split("_")[2]

    return site


def main():
    csv_file = filedialog.askopenfilename()
    file_name = get_site_name(csv_file)
    file_name = f"{file_name}.csv"
    print(file_name)

    data = get_csv_data(csv_file)
    data = split_names(data)
    print(create_csv_file(file_name, data))


if __name__ == "__main__":
    main()
