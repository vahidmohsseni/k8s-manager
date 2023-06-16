# Worker Node

## Running the application

By default, the node is configured to work with the linux image buil with [CVA6-SDK](https://github.com/openhwgroup/cva6-sdk), with the following requirements:

- python 3
- virtualenv

Due to the limited nature of said environment, some tinkering may be required in order to run this on your system.

Start the application with

```shell
python3 service.py --address <API address> --port <API port>
```
