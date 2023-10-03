#!/bin/bash

conda_env=""
if [ -z "$1" ]; then
  conda_env=" "
else
  conda_env=" -n $1 "
fi

eval "conda run --live-stream${conda_env}python main.py --http-port $APRS_SERVICE_HTTP_PORT --http-resource $APRS_SERVICE_HTTP_RESOURCE --use-rtl"
