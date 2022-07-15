#!/bin/sh

if [ -z "$1" ]
then
    echo "./req.sh create | delete "
    exit 1

elif [ "$1" = "create" ]
then
    curl -X POST -F "file=@hello.py" -F "cmd=python hello.py" -F "rt=None" http://localhost:5001/api/v1/tasks/first

elif [ "$1" = "delete" ]
then
    curl -X DELETE http://localhost:5001/api/v1/tasks/first

fi
