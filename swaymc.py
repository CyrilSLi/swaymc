import zmq, tkinter as tk

context = zmq.Context ()
socket = context.socket (zmq.REP)
socket.bind ("tcp://*:5555")
while True:
    msg = socket.recv ()
    socket.send (b"OK")
    print (msg.decode ())