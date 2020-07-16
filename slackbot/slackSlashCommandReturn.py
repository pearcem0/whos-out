import json
import os
import sys
import re
import requests
import datetime
from datetime import date
import base64
import numpy
import pandas as pd
import moment
import times
import boto3
from botocore.exceptions import ClientError

''' Who's Out Calls BambooHR's API to find out Who's Out Of Office,
    Group and Filter on employee information such as location or department.
    Results are returned matching the current date that the code is run.
'''
# Use secrets manager instead of putting secrets in lambda env vars stores as plain text 
def get_secret_variables():

    region_name = os.environ["region"]
    stage = os.environ["stage"]
    secret_name = "whosout-slackcommand-secrets-"+stage

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            print(
                "Secrets Manager can't decrypt the protected secret text using the provided KMS key."
            )

            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            print('An error occurred on the server side.')
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print('You provided an invalid value for a parameter.')
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print(
                'You provided a parameter value that is not valid for the current state of the resource.'
            )

            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("We can't find the resource that you asked for.")
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
                # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            return get_secret_value_response['SecretString']
        else:
            return base64.b64decode(get_secret_value_response['SecretBinary'])

secret = json.loads(get_secret_variables())
api_key = secret['bamboohr_api']
domain = secret['bamboohr_domain']

today = date.today()
formatted_date = today.strftime("%Y/%m/%d")
headers = {
            'accept': "application/json",
            'authorization': api_key
    }

# def parse_input():
#     print('parsing input...')

def get_help():
    return """
Type `/whosout` with no parameters to list all employees out of the office today.
Add a parameter to filter, possible filters include `location` and `department`
Add another parameter to filter based on the previous parameter, for example `/whosout location Manchester`"""


def lambda_handler(event, context):
    ''' Receive event and context from API Gateway
        Parse the body from Slack
        Decide what to do next
    '''
    
    event_data = json.dumps(event)
    print(event_data)
    event_data_dict = json.loads(event_data)
    
    body_encoded = str(event_data_dict['body'])
    body_decoded = str(base64.b64decode(body_encoded))
    # print(body_decoded)
    
    response_url_received = str(re.search('&response_url=(.*)&trigger_id', body_decoded).group(1))
    
    response_url_slashes_repl = response_url_received.replace("%2F", "/")
    response_url_colons_repl = response_url_slashes_repl.replace("%3A", ":")
    clean_url=response_url_colons_repl
    
    # Check the arguments to check if we need to group or filter
    # %21 equates to !
    cry_for_help = ["help", "help%21", "list"]
    no_help_needed=True
    dates = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "today", "this week", "next week", "tomorrow"]
    section = ""
    section_filter = ""
    args = filter_input_args(body_decoded)

    if len(args) > 0:
        if args[0].upper() in (cries.upper() for cries in cry_for_help):
            no_help_needed=False
            print('user called for help!')
        elif args[0].upper() in (date.upper() for date in dates):
            formatted_date = moment.date(args[0]).strftime("%Y/%m/%d")
            section = "allpeople"
            print('user provided a date.')
            print(formatted_date)
        else:
            section = args[0]
            print('section provided: ', section)
        if len(args) > 1:
            # argument may have spaces in.. this comes through as a + from the original event blob
            section_filter = args[1].replace("+"," ")
            print('section & filter provided: ', section, ' + ', section_filter)
        else:
            section_filter = "none"
    else:
        section = "allpeople"
        print('no section or filter provided, showing all employees.')
    
    if no_help_needed:
        formatted_date = today.strftime("%Y/%m/%d")
        result_output = getPeople(section, section_filter, formatted_date)
    else:
        result_output = get_help()
    # result_output = getPeople("allpeople", "none")
    # print(json.dumps(event.text))
    # print("Received event: " + json.dumps(event, indent=2))
    
    return_data = {'text': result_output,
    "response_type": "ephemeral"
    }

    slack_response = requests.post(
        clean_url, data=json.dumps(return_data),
        headers={'Content-Type': 'application/json'}
    )   
    if slack_response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )

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
    
def getPeople(section, section_filter, formatted_date):
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

    # except requests.exceptions.RequestException as e:  # This is the correct syntax
    #     print(e)
    #     sys.exit(1)
    people = json.loads(people_out.text)

    employee_ids = []
    employee_names = []
    for person in people:
        start_dt = datetime.datetime.strptime(person["start"], '%Y-%m-%d')
        end_dt = datetime.datetime.strptime(person["end"], '%Y-%m-%d')
        # if start_dt.date() <= date.today() and end_dt.date() >= date.today():
        if start_dt.date() <= datetime.datetime.strptime(formatted_date, '%Y/%m/%d').date() and end_dt.date() >= datetime.datetime.strptime(formatted_date, '%Y/%m/%d').date():
            try:
                if section == "allpeople":
                    name = person["name"]
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
            try:
                print('Listing Who\'s Out - Grouped by ' + section)
                output_message += 'Listing Who\'s Out - Grouped by ' + section

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
                        output_message += '\n-----------------'+'\n'+employee_sections+'\n'+'-----------------'
                        # pandas to_string defaults to right justify
                        print(grouping.displayName.to_string(index=False))
                        output_message += '\n'+grouping.displayName.to_string(index=False)
                    except:
                        print('\nError! Could not group by: ' + str(employee_sections))
                        output_message += '\nError! Could not group by: ' + str(employee_sections)
            except KeyError:
                output_message="""
Something went wrong getting a response from BambooHR :(
Type `/whosout help` for more examples or check BambooHR API documentation for possible Field Names."""
                print(output_message)

        else:
            print('-----------------'+'\n'+section_filter+'\n'+'-----------------')
            output_message += '-----------------'+'\n'+section_filter+'\n'+'-----------------'
            for employee_id in employee_ids:
                employee_info = getInfo(directory_in, employee_id, section)
                if employee_info == section_filter:
                    print(getInfo(directory_in, employee_id, "displayName"))
                    output_message += '\n'+getInfo(directory_in, employee_id, "displayName")
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

    return json.loads(full_dir.text)

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


