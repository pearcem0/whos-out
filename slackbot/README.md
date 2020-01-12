# Who's Out - Slackbot

Original script adapted to work as a Slack "Slash Command".

**In Progress...**

## Requirements
* AWS account available and profile setup to use via the CLI
* npm, python, pushd & popd

## Setup
* `npm install serverless@1.60.5`
* `npm install serverless-pseudo-parameters`
* `export AWS_PROFILE=<aws_profile_name>`
* Package the project
  * `pushd layers/pandas && chmod +x get_layer_packages.sh && ./get_layer_packages.sh && popd`
  * `serverless package --region <aws_region> --stage <development_stage>`
* Deploy the project
  * `serverless deploy --package .serverless --region <aws_region> --stage <development_stage>`
* The serverless project includes a Secrets Manager Secret (WhosOutSecrets) - after the first deployment make sure this is populated with two required keys:
  * `bamboohr_api`
    * This is the api key to use to communicate with the bamboohr api
  * `bamboohr_domain`
    * This is the company domain to retrieve information from using the bamboohr api

## Setup on Slack

Create an application and use the api gateway endpoint as the Request URL for a slash command.

The command may be something _like_ `/whosout [department or location] [filter (optional)]`

## Acknowledgements

* [Quy Tang sample Lambda Layer](layershttps://github.com/qtangs/sample-aws-lambda-layer)
* [KLayers Lambda Layers](https://github.com/keithrozario/Klayers/blob/master/deployments/python3.7/arns/eu-west-1.json)
