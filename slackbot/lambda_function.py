# TODO Work In Progress...

import json
import os
import sys
import re
import requests
import datetime
from datetime import date
import base64
# TODO pandas not included in vanilla lambda, create a layer or runtime
#import pandas as pd

''' Who's Out Calls BambooHR's API to find out Who's Out Of Office,
    Group and Filter on employee information such as location or department.
    Results are returned matching the current date that the code is run.
'''

today = date.today()
formatted_date = today.strftime("%Y/%m/%d")
headers = {
            'accept': "application/json",
            'authorization': os.environ["bamboohr_api"]
    }
domain = os.environ["bamboohr_domain"]

def lambda_handler(event, context):
    ''' Recieve event and context from API Gateway
        Parse the body from Slack
        Decide what to do next
    '''
    # print("Received event: " + json.dumps(event, indent=2))
    event_data = json.dumps(event)
    # print("Received event: " + event_data)
    event_data_dict = json.loads(event_data)
    body_encoded = str(event_data_dict['body'])
    body_decoded = str(base64.b64decode(body_encoded))
    # print(body_decoded)
    
    # Check the arguments to check if we need to group or filter
    section = ""
    section_filter = ""
    args = filter_input_args(body_decoded)

    if len(args) > 0:
        section = args[0]
        print('section provided: ', section)
        if len(args) > 1:
            section_filter = args[1]
            print('section & filter provided: ', section, ' + ', section_filter)
        else:
            section_filter = "none"
    else:
        section = "allpeople"
        print('no section or filter provided, showing all employees.')
    
    # TODO sort out the pandas depedency and make this dynamic!
    result_output = getPeople("allpeople", "none")
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': result_output
    }

def filter_input_args(user_text):
    user_text_in = user_text
    text_field = str(re.search('&text=(.*)&response_url', user_text_in).group(1))
    text_field_sliced = text_field.split("+",1)
    #make sure there are no empty items included in the list
    clean_text_field_sliced = list(filter(None, text_field_sliced))
    
    return clean_text_field_sliced
    
def getPeople(section, section_filter):
    ''' The getPeople function prints the list of employees that are Out Of Office,
        grouped and/or filtered based on user input.

        If the section provided is equal to "allpeople",
        the function simply calls the whos_out endpoint and prints the result.
        If a valid section (department, location etc.) is provided but filter is equal to "none",
        the function loads the employees and their section info info a dataframe (using Pandas),
        then sorts by section, then prints each group of sections.
        If a section is provided with a section filter (e.g. department, sales),
        the function only fetches information about that section and only prints matching sections.
    '''
    output_message = 'Who\'s Out - '+formatted_date+'\n'
    people_url = "https://api.bamboohr.com/api/gateway.php/"+domain+"/v1/time_off/whos_out/"
    people_querystring = {"start":formatted_date,"end":formatted_date}
    try:
        people_out = requests.request("GET", people_url, headers=headers, params=people_querystring)

    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print('Error making request to BambooHR API!:')
        print(e)
        sys.exit(1)
    people = json.loads(people_out.text)

    employee_ids = []
    employee_names = []
    for person in people:
        start_dt = datetime.datetime.strptime(person["start"], '%Y-%m-%d')
        end_dt = datetime.datetime.strptime(person["end"], '%Y-%m-%d')
        if start_dt.date() <= date.today() and end_dt.date() >= date.today():
            try:
                name = person["name"]
                if section == "allpeople":
                    employee_names.append(name)
                else:
                    employee_ids.append(person["employeeId"])
            except:
                print('error!')
    if section == "allpeople":
        employee_names.sort()
        # [print(i) for i in employee_names]
        for i in employee_names:
            output_message += "{}\n".format(i)
            
            
    else:
        directory_in = getDirectory()
        if section_filter == "none":
            print('Listing Who\'s Out - Grouped by ' + section)
            employee_df = pd.DataFrame({
                'displayName': [],
                section: []
            })
            sections_list = []

            for person_id in employee_ids:
                employee_name = getInfo(directory_in, person_id, "displayName")
                employee_section = getInfo(directory_in, person_id, section)

                if employee_section not in sections_list:
                    sections_list.append(employee_section)

                employee_df = employee_df.append({'displayName' : employee_name , section : employee_section}, ignore_index=True)

            employee_df_sorted = employee_df.sort_values(by=[section])
            groups = employee_df_sorted.groupby([section])
            for employee_sections in sections_list:
                try:
                    grouping = groups.get_group(employee_sections)
                    print('\n-----------------'+'\n'+employee_sections+'\n'+'-----------------')
                    # pandas to_string defaults to right justify
                    print(grouping.displayName.to_string(index=False))
                except:
                    print('\nError! Could not group by: ' + str(employee_sections))

        else:
            print('-----------------'+'\n'+section_filter+'\n'+'-----------------')
            for employee_id in employee_ids:
                employee_info = getInfo(directory_in, employee_id, section)
                if employee_info == section_filter:
                    print(getInfo(directory_in, employee_id, "displayName"))
                else:
                    employee_ids.remove(employee_id)
                    # remove from list in case we want to use the list again later

    return output_message
    
def getDirectory():
    ''' The getDirectory function simply calls the directory endpoint,
        which returns a list of employees.
        Then the function loads the json that is returned,
        so that it can be used to group and filter employees.
    '''
    dir_url = "https://api.bamboohr.com/api/gateway.php/"+domain+"/v1/employees/directory"
    try:
        full_dir = requests.request("GET", dir_url, headers=headers)

    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print('Error making request to BambooHR API!:')
        print(e)
        sys.exit(1)

    directory = json.loads(full_dir.text)
    return (directory)

def getInfo(directory_in, id, info_type):
    ''' The getInfo function gets the directory information for a single employee.
        The funtion requires - employee directory to filter through
        - employee id to select
        - field (info type) to return such as department, location, jobTitle etc.
    '''
    directory = directory_in
    for people in directory["employees"]:
        if people["id"] == str(id):
                return people[info_type]

