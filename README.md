# Container-Task Orchestrator
This software is consist of three main components based on the architecture that is illustrated below. 

![System Design](/design.png)

## Service Manager
The main component is `backend-service-manager` which has the features listed below.

- Handling the connection from `Executer`s
- Cheking the status of the connections 
- Keeping the connections alive
- Storing an incoming task and its metadata in memory
- Assigning a task to a free `Executer`
- Replyig to requests from API server

## API Server
As the name hints, its main feature is to provide an interface for users to interact with *Service Manager*. Follow this [link](api/README.md) to find more about the API endpoints.

## Executer Node
This piece of software is the part of the node/container/machine on which you want that task to be run. It constantly communicates with *Service Manager*, sends its status, and waits for a task to be assigned by keeping the socket connection open to the server. 
By decoupling this component from the *Service Manager*, we can scale out or in the runners according to the requirements of the load in the system. The time to wait for a runner to be up and running is eliminated by provisioning them before scheduling any tasks. Practically, we can add up as many runners as we need, and a single instance of the *Service Manager* will handle the load. 

## Deployment
It is possible to deploy the components manually or in a Kubernetes cluster. 
```shell
git pull https://github.com/vahidmohsseni/k8s-manager.git
cd k8s-manager/
```
### Kubernetes
TBD
### Manual
To run this system, follow the following instructions in order.
1. Service Manager 
```shell
cd backend-service-manager/
python service.py
```

2. Runners
    - It is possible to run multiple instances of this service on a same machine
```shell
cd frontend-service-manager/
python service.py
```

3. API Server
```shell
cd api/
python app.py
```
