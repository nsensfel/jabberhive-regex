#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

while true
do
   rm -f $1
   $SCRIPT_DIR/jabberhive-regex.py -s $1 -t $2 -f $3 -r $4 -x $5
   sleep 60
done
