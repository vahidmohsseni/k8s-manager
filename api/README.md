# API Server

## Running the server

### Docker

It is recommended to run the application using the docker-compose.yaml in the root directory.

```shell
docker-compose up -d
```

Should you wish to run the API Server solely, you can build the image with:

```shell
docker build -f Dockerfile -t k8s-manager-api .
```

and run the image with

```shell
docker run --env HOST=<0.0.0.0 or localhost> --env PORT=<port number> --env SOCKET_ADDRESS=<Service Manager address> k8s-manager-api
```

### Python standalone

You can also run the application as is:

```shell
python app.py
```

Customize the environment variables manually:

```shell
export HOST=<...>
export PORT=<...>
export SOCKET_ADDRESS=<...>
```

## List of available requests

| Explanation            | Route                                 | `curl` parameters                                                                                    |
| ---------------------- | ------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Get list of tasks      | [/api/v1/tasks/](#)                   | `-X GET`                                                                                             |
| Create a new task      | [/api/v1/tasks/<task_name>](#)        | `-X POST -F "file=@<filename>" -F "cmd=<args for python including file name>" -F "rt=<return type>"` |
| Delete a task          | [/api/v1/tasks/<task_name>](#)        | `-X DELETE`                                                                                          |
| Stop a task            | [/api/v1/tasks/<task_name>/stop](#)   | `-X POST`                                                                                            |
| Start a stopped task   | [/api/v1/tasks/<task_name>/start](#)  | `-X POST`                                                                                            |
| Check Status of a task | [/api/v1/tasks/<task_name>/status](#) | `-X GET`                                                                                             |

```

```
