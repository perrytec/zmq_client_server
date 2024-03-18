# zmq_python
A simple Server and Client wrapper for ZMQ Python.
Builds on top of `zmq`, `zmq.asyncio` to support an asynchronous server, and a sychrronous client.

Both Server and Client supports the Request-Reply, Push-Pull, and Publish-Subscribe message patterns.

-----
## Basic Usage

### ZmqClient
```
from zmq_python import ZmqClient

client = ZmqClient(
    sub_ip = "<pubsub_socket_ip>",
    push_ip = "<pushpull_socket_ip>",
    req_ip = "<requestreply_socket_ip>"
)
```

### ZmqServer
```
from zmq_python import ZmqServer

client = ZmqServer(
    pub_ip = "<pubsub_socket_ip>",
    pull_ip = "<pushpull_socket_ip>",
    rep_ip = "<requestreply_socket_ip>"
)
```