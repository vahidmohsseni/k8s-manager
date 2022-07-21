#!/bin/sh

# set a variable name task to first
task=first
echo $task
if [ -z "$1" ]
then
    echo "./req.sh create | delete | stop "
    exit 1

elif [ "$1" = "create" ]
then
    curl -X POST -F "file=@hello.py" -F "cmd=hello.py 6" -F "rt=None" http://localhost:5001/api/v1/tasks/first

elif [ "$1" = "delete" ]
then
    curl -X DELETE http://localhost:5001/api/v1/tasks/first

elif [ $1 = "stop" ]
then
    curl -X POST http://localhost:5001/api/v1/tasks/first/stop
fi
