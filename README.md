# Who's Out

[![GNU Public License](https://img.shields.io/badge/license-GPL%20(%3E%3D%203)-blue)]( https://www.gnu.org/licenses/gpl-3.0.en.html)

[![Tested on Python 3.7](https://img.shields.io/badge/Tested%20-Python%203.7-blue)]( https://www.python.org/downloads)

![BambooHR logo](bamboohr_logo.png)

[**TL;DR** - Examples](#examples)

Call BambooHR's API to find out who is currently Out Of Office. Group and filter on employee information such as location or department.
Results are returned matching the current date that the code is run.

The application prints the list of employees that are Out Of Office, grouped and/or filtered based on user input.

The application can be run with no arguments and simply calls the whos_out endpoint and prints the result in sorted in alphabetical order.

`python3 whos-out.py`

The application can also be provided with a 'section' parameter, this corresponds to the available fields for an employee - some of the default fields include jobTitle, gender etc. but you may also have some customer fields configured for you such as location or department. Information about the available fields can be found in the [bamboohr api reference guide](https://documentation.bamboohr.com/reference#get-employees-directory-1)

If a valid section (department, location etc.) is provided but no section filter is passed in as a parameter, the application loads the employees and the information about the section provided into a dataframe (using [Pandas](https://pandas.pydata.org/), then sorts by section, then prints each group of sections (grouped to make it more readable).

`python3 whos-out.py department`

If a section is provided with a section filter (e.g. department and sales), the application fetches information about that section and only prints matching sections. In this example the application would only list employees from the sales department that are Out Of Office today.

`python3 whos-out.py department sales`

## Requirements & Prerequisites

* valid Auth Token from BambooHR, with the relevant permissions to query who's out and employee directory

  * export this as an environment variable
  `export bamboohr_api=XXXXX`

* your bamboohr domain

  * export this as an environment variable
  `export bamboohr_domain=XXXXX`

* install required python modules - this project used [pip env](https://pipenv.readthedocs.io/en/latest/) but you can also install any modules you do not already have installed using [pip](https://pypi.org/project/pip/).

## Running

* If you want to use pipenv you and run something *like* `pipenv run python whos-out.py`

  * or just run`python3 whos-out.py` to run manually

### Examples

**Just list all employees out today**
`python3 whos-out.py`

``` text
Who's Out - 2019/12/26

Adam Ant
Jack Wills
John Smith
Martha Owens
Sandra Jones

```

**Group by section**
*where department is the section (passed in as parameter)*
`python3 whos-out.py department`

``` text
Who's Out - 2019/12/26

Listing Who's Out - Grouped by department

-----------------
Sales
-----------------
     Adam Ant

-----------------
Data Science
-----------------
  Martha Owens
  Sandra Jones

-----------------
Engineering UK
-----------------
    Jack Wills
    John Smith
 ```

**Filter by section**
*where location is the section (passed in as a parameter), which will be filtered by section filter (passed in as a parameter) the  to only show employees based in Manchester*
`python3 whos-out.py location Manchester`

``` text
Who's Out - 2019/12/26
-----------------
Manchester
-----------------

Jack Wills
John Smith
Sandra Jones
 ```

### Docker

There is also a Dockerfile provided, you can build this and run the image, passing in the environment variables - something *like* this...

`docker build -t whos-out .`
`docker run -e bamboohr_api=$bamboohr_api -e bamboohr_domainn=$bamboohr_domain whos-out python3 /whos-out.py`

## Gotchas

* [individual auth tokens only](https://documentation.bamboohr.com/docs#section-authentication) - BambooHR doesn't allow you to create system users to use a set api key, it must be authenticated and permissioned as if it were a real user of the software.

* due to the limitation of only using individual auth tokens, most users to not have the permissions required to query individual profiles, but are able to view the directory - at present the application uses the directory endpoint to get list of all employees in order to group and filters the list of employees returned by the whos out endpoint

## Reference

* [Information about using the BambooHR API](https://documentation.bamboohr.com/reference)
