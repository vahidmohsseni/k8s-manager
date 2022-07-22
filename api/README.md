# API Server
## List of available requests

|Explanation |Route|`curl` parameters|
|------------|-----|-----------------|
|Get list of tasks|[/api/v1/tasks/](#)|`-X GET`|
|Create a new task|[/api/v1/tasks/<task_name>](#)|`-X POST -F "file=@<filename>" -F "cmd=<args for python including file name>" -F "rt=<return type>"`|
|Delete a task|[/api/v1/tasks/<task_name>](#)|`-X DELETE`|
|Stop a task|[/api/v1/tasks/<task_name>/stop](#)|`-X POST`|
|Start a stopped task|[/api/v1/tasks/<task_name>/start](#)|`-X POST`|
|Check Status of a task|[/api/v1/tasks/<task_name>/status](#)|`-X GET`|