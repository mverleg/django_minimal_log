#!/usr/bin/env bash

function send_log ()
{
    # statuses are: error, warn, info, good (you could add more in MinimalLogEntry code if you want to)
    curl --silent --show-error --request POST 'https://example.com/log/add/' \
        --data-urlencode "description=$2" --data-urlencode "status=warn" \
        --data-urlencode 'key=@fe3=eX6r#6AF%68XTW,V_sbdxT=,S95';
}


