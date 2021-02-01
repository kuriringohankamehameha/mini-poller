# mini-poller

A simple demonstration of how polling can be done asyncronously as a service.
This uses `async` methods from Python, publishes messages into a Message Queue (_RabbitMQ_ is used here) and inserts persistent content into _MongoDB_.

***********

## Instructions

Before running this program, you need to have Docker installed on your machine.

Start all containers for this service using:

```bash
cd mini-poller
docker-compose up -d
```

All necessary setup will be done automatically by Docker.

Now open 2 different terminals, for spawning both the producer and the consumer

You need to connect to the `app` docker container from both the terminals:

```bash
docker exec -it mini_poller_app_1 /bin/bash # On both terminal 1 and terminal 2
```

On the first terminal, start the consumer:

```bash
cd /usr/src/app
python poll_service.py
```

On the second terminal, start the core service:

```bash
cd /usr/src/app
python poll_consumer.py
```

Immediately, you'll start observing the polling changes in action!

***************

## Methodology

* There are two programs:
1. `poll_service.py`: Consists of the main service, which does the actual polling and publishes messages
2. `poll_consumer.py`: A listener which retrieves incoming messages and stores them into DB.

The poll service basically keeps requesting a list of API endpoints and publish messages into RabbitMQ.

The poll consumer will keep listening to incoming messages on that channel and insert any records into MongoDB directly.

***************