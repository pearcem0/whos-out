# @TODO

- [ ] Keep track of the validation token Slack gives you when the command is created. Always validate the token field in an incoming slash command request has been issued to you by Slack.
- [ ] Consider fetching list of possible sections from bamboo to validate user input and provide useful help text?
- [ ] Check the command in the event blob and use that to make the help text dynamic
- [ ] Find some way to match user input and sections in bamboo regardless of capitalisation i.e. sales or Sales.
- [ ] Better error handling for network errors, timeout etc. that cause slack command to fail(?)
- [ ] Only fetch tokens from secret manager if required i.e. not needed if just asking for help
- [ ] Return a proper response if no results are found.
- [ ] Add test events to mock calls from slack user agent.
- [ ] Personalise the response using user_id or user_name from event blob?
- [X] Parse section filters properly in case of symbols or spaces e.g "Data Science"
- [X] Send slack a response straight away (3s), to avoid "operation_timeout", then return response when finished