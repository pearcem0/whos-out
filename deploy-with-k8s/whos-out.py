from flask import Flask
import os
import requests
import json
import os
import sys
import datetime
from datetime import date
import pandas as pd

''' Who's Out Calls BambooHR's API to find out Who's Out Of Office, 
    Group and Filter on employee information such as location or department.

    Results are returned matching the current date that the code is run.
'''

app = Flask(__name__)

today = date.today()
formatted_date = today.strftime("%Y/%m/%d")

if "bamboohr-domain" in os.environ:
    pass
if "bamboohr-api" in os.environ:
    pass

headers = {
            'accept': "application/json",
            'authorization': os.environ["bamboohr-api"]
    }
domain = os.environ["bamboohr-domain"]

section = ""
section_filter = ""

@app.route('/')
def index():
    print('working...\n')
    return domain+' | Who\'s Out - '+formatted_date+'\n'

# @app.route('/all')
# def list_by_deparment():
#     dir_url = "https://api.bamboohr.com/api/gateway.php/"+domain+"/v1/time_off/whos_out/"
#     try:
#         full_dir = requests.request("GET", dir_url, headers=headers)
    
#     except requests.exceptions.RequestException as e:  # This is the correct syntax
#         print('Error making request to BambooHR API!:')
#         print(e)
#         sys.exit(1)

#     return json.loads(full_dir.text)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
