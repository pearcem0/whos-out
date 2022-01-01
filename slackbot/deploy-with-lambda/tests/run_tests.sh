#!/bin/bash

for test in lambda_test_events/example_body/*.txt
do
    echo encoding $test...
    encoded_body=`cat $test | base64`
    #echo $encoded_body
    cmd="sed 's/<body>/$encoded_body/' lambda_test_events/body_template.json > lambda_test_events/temp_test.json"
    create_temp_test_file=$(eval $cmd)
    cd .. && cat tests/lambda_test_events/temp_test.json | sls --stage prod --region eu-west-1  invoke local --function slackSlashCommand
    cd tests/
    rm lambda_test_events/temp_test.json
done