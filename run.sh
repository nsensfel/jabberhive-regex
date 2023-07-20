#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

while true
do
   rm -f $1
   $SCRIPT_DIR/jabberhive-regex.py -s $1 -t $2 -f $3 -r "$(cat $SCRIPT_DIR/capture_pattern.txt)" -x "$(cat $SCRIPT_DIR/replace_pattern.txt)"
   sleep 60
done
