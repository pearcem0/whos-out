# Who's Out - Slackbot

Who's Out Calls BambooHR's API to find out Who's Out Of Office, Group and Filter on employee information such as location or department. Results are returned matching the current date that the code is run.

[Original script](../../basic-script-docker/whos-out.py) adapted to work as a Slack "Slash Command".
Deployed using AWS Lambda - some code/deployment steps may be required.

**In Progress...**

Well, unfinished. 🙄😳
Intended as an fairly quick experiment, and to speed up the process of checking if a colleague is out of office.

## Requirements
* AWS account available and profile setup to use via the CLI
* npm, python, pushd & popd

## Setup

Deployed as AWS Lambda functions exposed using Amazon API Gateway using the [Serverless framework](https://serverless.com/), and then setup as a 'slash command' in [Slack](https://slack.com/).

### Things to note

* Note the use of Lambda layers for packaging up the python libraries `moment` and `pandas`.
* Slack expects a pretty quick response from the first API call, which isn't possible - so I've split the applicaiton into separate lambda functions - one to let Salck know we are thinking about it and then pass on the request/event details to the second lambda to get the results. 

* `npm install serverless@1.60.5`
* `npm install serverless-pseudo-parameters`
* `export AWS_PROFILE=<aws_profile_name>`
* Package the project
  * `pushd layers/pandas && chmod +x get_layer_packages.sh && ./get_layer_packages.sh && popd`
  * `pushd layers/moment && chmod +x get_layer_packages.sh && ./get_layer_packages.sh && popd`
  * `serverless package --region <aws_region> --stage <development_stage>`
* Deploy the project
    * `serverless deploy --package .serverless --region <aws_region> --stage <development_stage>`
  * Deploy one function at a time (quicker!)
    * `serverless deploy --package .serverless --region <aws_region> --stage <development_stage> -f <function_name>`
* The serverless project includes a Secrets Manager Secret (WhosOutSecrets) - **after the first deployment make sure this is populated with two required keys**:
  * `bamboohr_api`
    * This is the api key to use to communicate with the bamboohr api
  * `bamboohr_domain`
    * This is the company domain to retrieve information from using the bamboohr api

## Setup on Slack

Create an application and use the API gateway endpoint as the Request URL for a slash command.
You can check the API gateway url on the AWS console after deploying, make sure you include the full resource path when you fill in the Request URL for the slash command, for example _https://<api-id>.execute-api.<region>.amazonaws.com/<stage>/whosout-<stage>-slackSlashCommand_.

The command may be something _like_ `/whosout [department or location (optional)] [filter (optional)]` or `/whosout help`

## Acknowledgements

* [Quy Tang sample Lambda Layer](https://github.com/qtangs/sample-aws-lambda-layer)
* [KLayers Lambda Layers](https://github.com/keithrozario/Klayers/blob/master/deployments/python3.7/arns/eu-west-1.json)
