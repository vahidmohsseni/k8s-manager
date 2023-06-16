# Worker Node

## Running the application

By default, the node is configured to work with the linux image built with [CVA6-SDK](https://github.com/openhwgroup/cva6-sdk), with the following requirements:

- python 3
- virtualenv

Due to the limited nature of said environment, some tinkering may be required in order to run this on your local system.

Start the application with

```shell
python3 service.py --address <manager address> --port <manager port>
```

## Worker arguments

| Argument              | Explanation                                                                   |
| :-------------------- | :---------------------------------------------------------------------------- |
| `-a`,<br/>`--address` | IP address of the target Service Manager server.<br/>Defaults to `localhost`. |
| `-p`<br/>`--port`     | Port used by the target Service Manager server.<br/> Defaults to `5556`.      |
