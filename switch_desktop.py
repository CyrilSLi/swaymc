import sys, subprocess, json, zmq

context = zmq.Context ()
socket = context.socket (zmq.REQ)
socket.connect ("tcp://localhost:5555")

if len (sys.argv) != 2:
    sys.exit (1)
action = sys.argv [1].lower ()
if action not in ("left", "right"):
    sys.exit (1)

socket.send (action.encode ())

spaces = subprocess.run (["swaymsg", "-t", "get_workspaces"], capture_output = True)
spaces.check_returncode ()
spaces = json.loads (spaces.stdout.decode ())

for i in spaces:
    if i ["focused"]:
        display, num = i ["output"], i ["num"]
        break
else:
    sys.exit (1)

spaces = [i ["num"] for i in spaces if i ["output"] == display]
num = spaces.index (num)

if action == "left":
    num = spaces [max (num - 1, 0)]
else:
    num = spaces [min (num + 1, len (spaces) - 1)]

try:
    socket.recv (flags = zmq.NOBLOCK)
except zmq.Again:
    subprocess.run (["swaymsg", "workspace", str (num)])