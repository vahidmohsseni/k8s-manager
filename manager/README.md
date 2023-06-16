# Service Manager

## Running the manager

### Docker

It is recommended to run the application using the docker-compose.yaml in the root directory.

```shell
docker-compose up -d
```

Should you wish to run the manager service solely, you can build the image with:

```shell
docker build -f Dockerfile -t k8s-manager-service .
```

and run the image with

```shell
docker run -p 5555:5555 -p 5556:5556 k8s-manager-service
```

### Python standalone

You can also run the application as is:

```shell
python service.py
```

#### Ports

The application by default relies on two ports:

- 5555 for pyzmq traffic
- 5556 for node management
