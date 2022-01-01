# Testing

You can use serverless to invoke the function locally, but you'll need to pass it a body. This includes things like user input, where the call is coming from etc. There are a **mock** few examples in the `tests/lambda_text_events` directory in this repo.

The main part of the example call is the **body** section of the json. Slack sends the body as a base64 encoded string. See the `example_body.json` for mock decoded strings, take note of the fields such as `command` and `text` that is used to strip out of the body to read the users input. 

## Locally

### Automated

run `run_tests.sh` script.

### Testing Manually

Read an example event file into serverless to invoke the function locally.

`cat lambda_test_events/example_body.json | sls --stage prod --region eu-west-1  invoke local --function slackSlashCommand`

You should get a result something like this:
```
{
    "statusCode": 200,
    "headers": {
        "Content-Type": "text/plain"
    },
    "body": "\nType `/whosout` with no parameters to list all employees out of the office today.\nAdd a parameter to filter, possible filters include `location` and `department`\nAdd another parameter to filter based on the previous parameter, for example `/whosout location Manchester`"
}
```
The body being returned is what gets returned to the user ins slack, if the call was successful.

## Deployed

When the service is deployed, installed to Slack and running you can of course call the function using slack, but typing something like:

`/whosout help`

`/whosout`

`/whosout today`

`/whosout tomorrow`

`/whosout department`

`/whosout deparment Sales`

`/whosout location`

`/whosout location Jaipur`