Clear instructions for how to programmatically REQUEST data from the microservice you implemented.

To REQUEST data, ZEROMQ will be used create a socket of type request, connects and starts sending messages.
###############
import zmq

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

#  Do 10 requests, waiting each time for a response
for request in range(10):
    print(f"Sending request {request} …")
    socket.send(b"Hello")

    #  Get the reply.
    message = socket.recv()
    print(f"Received reply {request} [ {message} ]")
###############

Clear instructions for how to programmatically RECEIVE data from the microservice you implemented. Include an example call.

To RECEIVE data, ZEROMQ will be used to create a socket of type response and bind it to a port and then waits for messages.
If no messages are present the method will block.
###############
import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    #  Wait for next request from client
    message = socket.recv()
    print(f"Received request: {message}")

    #  Do some 'work'
    time.sleep(1)

    #  Send reply back to client
    socket.send(b"World")
###############

