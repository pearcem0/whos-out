# A very simple starting point...

The original starting point, trying out what could be done with the bamboo hr api.

Along with a very simple dockerfile for containerising the app.

## Running as a standalone script

* Set the requirement environment variables:
  * `export bamboohr_domain=<BAMBOO HR DOMAIN HERE>`
    * Example - `export bamboohr_domain=acmecorp`
  * `export bamboohr_api=<API KEY HERE>`
    * Example - `export bamboohr_api=aaaa-1112323-assds`
* Run the script:
  * `python3 whos-out.py`

## Running as a docker container

* Build the Docker image:
  * `docker built -t <whatever-you-want-to-name-the-image> .`
    * Example - `docker built -t whos-out .`
* Run the Docker image as a container, passing in the environment variables:
  * `docker run -e bamboohr_domain=<BAMBOO HR DOMAIN HERE> -e bamboohr_api=<API KEY HERE> <whatever-you-want-to-name-the-image>`
    * Example - `docker run -e bamboohr_domain=acmecorp -e bamboohr_api=aaaa-1112323-assds whos-out`
