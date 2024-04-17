import os
import csv
import json
import sys

# Python script to process salary guide data 
# This was written specifically so that it only uses functions available in the standard Python library. 
# As a result, this script is a giant pile of spaghetti code that is basically unreadable. 
# Refer to function documentations below to understand functionality as well as salary guide script documentation (to be written).

# Command line usage: python salary_parser.py [input csv file path] [output json file path] ['-posType' optional flag: adds 'positionType' labels]

args = sys.argv
if len(args) < 3:
    raise ValueError("You must specify at least 2 arguments when running this script, with the first being the input path, and the second being the output path.")

# The filepath for the input (.csv) data:
INPUT_CSV_PATH = args[1]

# The output filepath (i.e. for the .json file)
# Note, the file path must already be valid (i.e. folders specified must already exist)
OUTPUT_CSV_PATH = args[2]

# Handling flag for whether to parse and add 'positionType' values
POS_TYPE_FLAG = False

if len(args) >= 4 and args[3] == "-posType":
    POS_TYPE_FLAG = True

# If there's a problem with reading the file in, check if this is the correct encoding: 
TEXT_ENCODING = "utf-8-sig"

# PAY_CODES is unused since this it is incomplete
PAY_CODES = {
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


# processing Graybook salaries
def parse_salaries_(csv_path: str) -> list[dict]:
    """Function to process UI salary data from a CSV file (see template). Saves result in JSON file to be used by the DI salary guide widget.
    Note: one CSV file per campus/unit (i.e. UIUC, UIC, UIS, and UI System each have their own seperate CSV file with respective salary data)\n
    Args:
        csv_path (str): the file path for the CSV
    Return:
        A list of dicts, which, when dumped into a JSON file, can be loaded by the salary guide widget\n\n
    
    Returned `list[dict]` has following structure:

    [
        { # these dicts are referred to as 'employee dicts'
            "name": employee_name,
            "salary": employee_total_salary_as_float,
            "positions": [ 
                # dicts in this list are referred to as 'position dicts'
                {
                    "title": position_title,
                    "department": position_dept,
                    "college": position_college,
                    "positionSalary": position_salary_as_float,
                    "tenure": tenure_status, # see 'tenure_codes'
                    "payType": paycode
                }, 
                ... 
            ]
        },
        ...
    ]

    Internally, this function uses the tuple (employee_name, employee_total_salary_as_string) as a makeshift primary key to track each employee/employee dict.
    """
    
    all_empls_dict = {} # main dict used to keep track of everything, has structure: {tuple_key:{employee dict}} where tuple_key is the makeshift primary key
    
    row_idx = 1 # setting start index at 1 for easier debugging since Excel row labels start at 1
    with open(csv_path, encoding=TEXT_ENCODING) as data_raw:
        data_reader = csv.DictReader(data_raw)
        print("CSV opened successfully...")
        for row in data_reader:
            # ignores empty rows in CSV
            if all(string == "" for string in row):
                continue

            # tuple key that acts as a unique identifier for each employee in all_empls_dict
            # the total salary is converted to string so as to avoid float comparison issues when checking dict keys
            tuple_key = (row["name"], "${:,.2f}".format(float(row["total_salary"])))

            # Checks if tuple key exists in all_empls_dict
            # If so, we add a dict containing info on the new position to the "positions" list for the corresponding employee in all_empls_dict
            if tuple_key in list(all_empls_dict.keys()): 

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
                curr_empl_dict = all_empls_dict[tuple_key]
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
                }]}
                # Adding the new employee dict to all_empls_dict
                all_empls_dict.update({tuple_key:curr_empl_dict})
            row_idx += 1
        data_raw.close()
        print(str(row_idx - 1) + " rows read")
    return list(all_empls_dict.values())

# Function that takes output of parse_salaries_() and adds 'positionType' labels for each position based on boolean parameters
# Note: This function is kind of still in beta/WIP, as it does not cover all position types, and also is not 100% reliable
def position_type_parser(record_dict_list:list[dict]) -> list[dict]:
    """
    Function that checks the value of the 'title' variable for each position dict and add a corresponding label/category to each position dict as 'positionType'
    Note: This function is kind of still in beta/WIP, as it does not cover all position types, and also is not 100% reliable.\n
    Args:
        record_dict_list: list of employee dicts (i.e. the output of parse_salaries_())
    Returns:
        list of employee dicts with added 'positionType' labels for each position dict
    """
    print("Parsing with 'positionType' labels...")
    for idx in range(len(record_dict_list)):
        record_dict = record_dict_list[idx]
        for pos_idx in range(len(record_dict['positions'])):
            title_token_list:list = record_dict['positions'][pos_idx]['title'].replace(',', '').replace('.', '').upper().split(' ')
            if any(['ASST', 'PROF'] == title_token_list[i:i+2] for i in range(len(title_token_list))) or any(['ASST', 'PROFESSOR'] == title_token_list[i:i+2] for i in range(len(title_token_list))):
                record_dict_list[idx]['positions'][pos_idx].update({'positionType':'ASST PROF'})
            elif any(['ASSOC', 'PROF'] == title_token_list[i:i+2] for i in range(len(title_token_list))) or any(['ASSOC', 'PROFESSOR'] == title_token_list[i:i+2] for i in range(len(title_token_list))):
                record_dict_list[idx]['positions'][pos_idx].update({'positionType':'ASSOC PROF'})
            elif 'PROF' in title_token_list or 'PROFESSOR' in title_token_list:
                record_dict_list[idx]['positions'][pos_idx].update({'positionType':'PROF'})
            elif 'LECTURER' in title_token_list or 'INSTRUCTOR' in title_token_list or 'INSTR' in title_token_list:
                record_dict_list[idx]['positions'][pos_idx].update({'positionType':'INSTRUCTOR'})
            elif 'POSTDOC' in title_token_list:
                record_dict_list[idx]['positions'][pos_idx].update({'positionType':'POSTDOC'})
            elif 'RES' in title_token_list and not ('DIR' in title_token_list or 'COORD' in title_token_list):
                record_dict_list[idx]['positions'][pos_idx].update({'positionType':'MISC RES'})
            elif 'SCHOLAR' in title_token_list:
                record_dict_list[idx]['positions'][pos_idx].update({'positionType':'MISC SCHOLAR'})
            elif 'DIRECTOR' in title_token_list or 'DIR' in title_token_list:
                record_dict_list[idx]['positions'][pos_idx].update({'positionType':'DIRECTOR'})
            elif 'COORDINATOR' in title_token_list or 'COORD' in title_token_list:
                record_dict_list[idx]['positions'][pos_idx].update({'positionType':'COORDINATOR'})
            elif 'MANAGER' in title_token_list or 'MGR' in title_token_list:
                record_dict_list[idx]['positions'][pos_idx].update({'positionType':'MANAGER'})
            elif 'SPECIALIST' in title_token_list or 'SPEC' in title_token_list:
                record_dict_list[idx]['positions'][pos_idx].update({'positionType':'SPECIALIST'})
            elif any(['OFFICE', 'SUPPORT'] == title_token_list[i:i+2] for i in range(len(title_token_list))):
                record_dict_list[idx]['positions'][pos_idx].update({'positionType':'OFFICE SUPPORT'})
            elif any(['BUILDING', 'SERVICE'] == title_token_list[i:i+2] for i in range(len(title_token_list))):
                record_dict_list[idx]['positions'][pos_idx].update({'positionType':'OFFICE SUPPORT'})
            elif 'COACH' in title_token_list:
                record_dict_list[idx]['positions'][pos_idx].update({'positionType':'COACH'})
            elif 'POLICE' in title_token_list:
                record_dict_list[idx]['positions'][pos_idx].update({'positionType':'POLICE'})
            else:
                record_dict_list[idx]['positions'][pos_idx].update({'positionType':'OTHER'})
    return record_dict_list

# Function that basically puts it all together and dumps the result into a JSON file at the provided output path
def process_salary_data(input_csv_path: str, output_json_path: str):
    """Wrapper function that basically just calls parse_salaries_() and dumps the result into a JSON file at the provided output path.
    Args:
        csv_path (str): the file path for the CSV
        output_path (str): the output file path for the JSON
    """
    if os.path.isfile(input_csv_path):
        if POS_TYPE_FLAG:
            parsed_dict = position_type_parser(parse_salaries_(input_csv_path))
        else:
            print("Parsing...")
            parsed_dict = parse_salaries_(input_csv_path)
    else:
        raise FileNotFoundError("File \'" + input_csv_path + "\' does not exist. Please ensure that the input filepath is correct")
    
    print("Writing data to file at: " + output_json_path)
    with open(output_json_path, "w+", encoding='utf-8') as out:
        # Takes the values the list, and dumps it into a JSON file.
        json.dump(sorted(parsed_dict, key=lambda d: d['name']), out, indent='\t')
        out.close()

process_salary_data(INPUT_CSV_PATH, OUTPUT_CSV_PATH)