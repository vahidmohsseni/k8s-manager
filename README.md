# Container-Task Orchestrator

This software is consist of three main components based on the architecture that is illustrated below.

![System Design](/.github/images/design.png)

## Service Manager

The main component is `backend-service-manager` which has the features listed below.

- Handling the connection from `Executer`s
- Cheking the status of the connections
- Keeping the connections alive
- Storing an incoming task and its metadata in memory
- Assigning a task to a free `Executer`
- Replyig to requests from API server

## API Server

As the name hints, its main feature is to provide an interface for users to interact with _Service Manager_. Follow this [link](api/README.md) to find more about the API endpoints.

## Executer Node

This piece of software is the part of the node/container/machine on which you want that task to be run. It constantly communicates with _Service Manager_, sends its status, and waits for a task to be assigned by keeping the socket connection open to the server.
By decoupling this component from the _Service Manager_, we can scale out or in the runners according to the requirements of the load in the system. The time to wait for a runner to be up and running is eliminated by provisioning them before scheduling any tasks. Practically, we can add up as many runners as we need, and a single instance of the _Service Manager_ will handle the load.

# Docker images

For convenience, you can start the cloud containers with docker compose:

```shell
docker compose up --build -d
```

## Building individual containers

Build and run the API image

```shell
cd api
docker build -f Dockerfile -t k8s-manager-api .
docker run -p 5001:5001 --env HOST=0.0.0.0 -d k8s-manager-api

```

Build and run the service manager image

```shell
cd manager
docker build -f Dockerfile -t k8s-manager-service .
docker run -d k8s-manager-service
```

### Manual deployment

To run this system, follow the following instructions in order.

1. Service Manager

```shell
cd manager
python service.py
```

2. API Server

```shell
cd api
python app.py
```

3. Runners
   - It is possible to run multiple instances of this service on a same machine

```shell
cd worker
# Run on localhost
python service.py

# Connect to external host
python3 service.py -a <host address> -p <port>
```


##  Acknowledgement
This project has received funding from the Key Digital Technologies Joint Undertaking (KDT JU) under grant agreement No 877056. The JU receives support from the European Union’s Horizon 2020 research and innovation programme and Spain, Italy, Austria, Germany, Finland, Switzerland.

![FRACTAL Logo](https://cloud.hipert.unimore.it/apps/files_sharing/publicpreview/jHmgbEb2QJoe8WY?x=1912&y=617&a=true&file=fractal_logo_2.png&scalingup=0)

![EU Logo](https://cloud.hipert.unimore.it/apps/files_sharing/publicpreview/pessWNfeqBfYi3o?x=1912&y=617&a=true&file=eu_logo.png&scalingup=0)
![KDT Logo](https://cloud.hipert.unimore.it/apps/files_sharing/publicpreview/yd7FgKisNgtLPTy?x=1912&y=617&a=true&file=kdt_logo.png&scalingup=0)  
