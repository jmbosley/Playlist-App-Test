# Request
To REQUEST data, ZEROMQ will be used create a socket of type request, connects and starts sending messages.

```
import zmq
context = zmq.Context()
#  Socket to talk to server
context = zmq.Context()
#  Socket to talk to server
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:8000")

message = (playlist +":"+ songA +":"+ songB).encode("utf-8")
socket.send(message)

#  Get the reply.
message = socket.recv()
```
# Receive

Clear instructions for how to programmatically RECEIVE data from the microservice you implemented. Include an example call.

To RECEIVE data, ZEROMQ will be used to create a socket of type response and bind it to a port and then waits for messages.
If no messages are present the method will block.
```
import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:8000")


while True:
    #  Wait for next request from client
    message = socket.recv()
    stringMessage = message.decode("utf-8")
    messageSplit = stringMessage.split(':')

    socket.send(b"Complete")


```
![UML sequence diagram showing how requesting and receiving data works](/Sequence_Diagram.png)
