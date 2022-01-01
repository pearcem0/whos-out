# Example message body

The main part of the example call is the **body** section of the json. Slack sends the body as a base64 encoded string.

These are mock decoded strings, take note of the fields such as `command` and `text` that is used to strip out of the body to read the users input.

## Automated testing

These `.txt` files can be used to substitute body key in `../body_template.json` and pass into `sls invoke` to run the function locally with that mock event data.