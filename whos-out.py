#!/usr/local/bin/python3

import json
import os
import sys
import requests
import datetime
from datetime import date
import pandas as pd

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

section = ""
section_filter = ""

# Check the arguments to check if we need to group or filter
if len(sys.argv) > 1:
    section = sys.argv[1]
    if len(sys.argv) > 2:
        section_filter = sys.argv[2]
    else:
        section_filter = "none"
else:
    section = "allpeople"

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
        [print(i) for i in employee_names] 
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

def main():
    print('Who\'s Out - '+formatted_date+'\n')
    getPeople(section, section_filter)

if __name__== "__main__":
    main()
