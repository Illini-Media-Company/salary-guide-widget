import os
import csv
import json

# Python script to process salary guide data 
# This was written specifically so that it only uses functions available in the standard python library

# Set this path to the folder which contains the salary data csv files for all the campuses:
# Note, the file path must already be valid (i.e. the folders specified must already exist)
INPUT_CSV_PATH = "input/UIS.csv"

# Set this path to the folder which you want the script to output the corresponding .json files:
# Note, the file path must already be valid (i.e. folders specified must already exist)
OUTPUT_CSV_PATH = "output/UIS.json"

# If there's a problem with reading the file in, check if this is the correct encoding: 
TEXT_ENCODING = "utf-8-sig"

# EMPL_CLASSES is unused since this it is incomplete
EMPL_CLASSES = {
    "AA":"Academic 9/12 month Benefit Eligible (9 months service paid over 12 month period)",
    "AB":"Academic 9/12 month Non-Benefit Eligible (9 months service paid over 12 month period)",
    "AG":"Academic 10/12 month Benefit Eligible (10 months service paid over 12 month period)",
    "AH":"Academic 10/12 month Non-Benefit Eligible (10 months service paid over 12 month period)",
    "AL":"Academic 12 month Benefit Eligible (12 months service paid over 12 month period)",
    "AM":"Academic 12 month Non-Benefit Eligible (12 months service paid over 12 month period)",
    "BA":"Academic Professional 12 month Benefit Eligible (12 months service paid over 12 month period)",
    "BB":"Academic Professional 12 month Non-Benefit Eligible (12 months service paid over 12 month period)",
    "BC":"Academic Professional 9/12 month Benefit Eligible (9 months service paid over 12 month period)",
    "BD":"Academic Professional 9/12 month Non-Benefit Eligible (9 months service paid over 12 month period)",
    "BG":"Academic Professional 10/12 month Benefit Eligible (10 months service paid over 12 month period)",
    "BH":"Academic Professional 10/12 month Non-Benefit Eligible (10 months service paid over 12 month period)",
    "PA":"Postdoctoral Research Associate Benefit Eligible (Service paid over 12 month period)",
    "PB":"Postdoctoral Research Associate Non-Benefit Eligible (Service paid over 12 month period)"
}

# Dict for tenure codes -- see Graybook documentation
tenure_codes = {
    "A":"Indefinite tenure",
    "M":"Multi-Year Contract Agreement",
    "N":"Initial/Partial Term",
    "P":"Probationary Term",
    "Q":"Specified Term Appointment",
    "T":"Terminal Contract",
    "W":"Special Agreement to Accept Academic Appointment and Reappointment for Definite Term"
}

""" 
all_empls_dict has structure: 
{
    (employee1_name, employee1_total_salary_as_string) : {
        "name": employee1_name,
        "salary": employee1_total_salary_as_float_2f,
        "positions": [
            {
                "title": position_title,
                "department": position_dept,
                "college": position_college,
                "positionSalary": position_salary_as_float_2f,
                "tenure": tenure_status (see 'tenure_CODES'),
                "payType": paycode
            }, ... ]
        ]
    },
    (employee2_name, employee2_salary_as_string) : { See above }...
}
We use a tuple of (employee_name_string, employee_total_salary_string) as a makeshift primary key
"""

# processing Graybook salaries
def parse_salaries_(csv_path: str) -> list:
    """Function to process UI salary data from a CSV file (see template). Saves result in JSON file to be used by the DI salary guide widget.
    Note: one CSV file per campus/unit (i.e. UIUC, UIC, UIS, and UI System each have their own seperate CSV file with respective salary data)
    Args:
        csv_path (str): the file path for the CSV being processed relative to the folder containing this script
    Return:
        A list of dicts, which, when dumped into a JSON file, can be loaded by the salary guide widget
    """
    
    all_empls_dict = {}
    
    row_idx = 1 # setting start index at 1 for easier debugging since Excel row labels start at 1
    with open(csv_path, encoding=TEXT_ENCODING) as data_raw:
        data_reader = csv.DictReader(data_raw)
        print("\nCSV opened successfully...")
        for row in data_reader:
            # ignores empty rows in CSV
            if all(string == "" for string in row):
                continue
            #print(row)
            # Checks if tuple key exists in all_empls_dict
            # If so, we add a dict containing info on the new position to the "positions" list for the corresponding employee in all_empls_dict
            if (row["name"], "${:,.2f}".format(float(row["total_salary"]))) in list(all_empls_dict.keys()):
            # (the total salary is converted to string so as to avoid float comparison issues when checking dict keys)

                # Creating the dict with new position info
                curr_pos_dict = {
                    "title":row["position_title"],
                    "department":row["department"],
                    "college":row["college"],
                    "positionSalary":float(row["position_salary"]),
                    "tenure":tenure_codes.get(row["tenure"], ""),
                    "payType":row["pay_type"]
                }
                # Adding the new position dict to all_empls_dict
                curr_empl_dict = all_empls_dict[(row["name"], "${:,.2f}".format(float(row["total_salary"])))]
                curr_empl_dict["positions"].append(curr_pos_dict)
            
            # If the tuple key does not exist, we create a new entry in all_empls_dict using the tuple key
            else:
                curr_empl_dict = {
                    "name":row["name"],
                    "salary":float(row["total_salary"]),
                    "positions":[{
                        # Adding position dict in "positions" for the position info
                        "title":row["position_title"],
                        "department":row["department"],
                        "college":row["college"],
                        "positionSalary":float(row["position_salary"]),
                        "tenure":tenure_codes.get(row["tenure"], ""),
                        "payType":row["pay_type"]
                }]
                }
                # Adding the new employee dict to all_empls_dict
                all_empls_dict.update({(row["name"], "${:,.2f}".format(float(row["total_salary"]))):curr_empl_dict})
            row_idx += 1
        data_raw.close()
        print("\n" + str(row_idx - 1) + " rows read")
    return list(all_empls_dict.values())

# Function that basically puts it all together and dumps the result into a JSON file at the provided output path
def process_salary_data(input_csv_path: str, output_json_path: str):
    """Wrapper function that basically just calls parse_salaries_() and dumps the result into a JSON file at the provided output path.
    Args:
        csv_path (str): the file path for the CSV being processed relative to the folder containing this script
        output_path (str): the output file path for the JSON relative to the folder containing this script
    """
    if os.path.isfile(input_csv_path):
        parsed_dict = parse_salaries_(input_csv_path)
    else:
        raise FileNotFoundError("File \'" + input_csv_path + "\' does not exist. Please ensure that 'INPUT_CSV_PATH' is correct")
    
    print("Writing data to file at: " + output_json_path)
    with open(output_json_path, "w+", encoding='utf-8') as out:
        # Takes the values of all_empls_dict as a list, and dumps it into JSON. (Keys of all_empls_dict are ignored)
        json.dump(sorted(parsed_dict, key=lambda d: d['name']), out, indent='\t')

process_salary_data(INPUT_CSV_PATH, OUTPUT_CSV_PATH)