import zmq, threading, json, subprocess, time, tkinter as tk

context = zmq.Context ()
socket = context.socket (zmq.REP)
socket.bind ("tcp://*:5555")

outputs = subprocess.run (["swaymsg", "-t", "get_outputs", "-r"], capture_output = True)
outputs.check_returncode ()
outputs = json.loads (outputs.stdout.decode ())
scales = {i ["name"]: str (i ["scale"]) for i in outputs}
outputs = {i ["name"]: (i ["rect"] ["width"], i ["rect"] ["height"]) for i in sorted (outputs, key = lambda x: x ["focused"])}

workspaces = subprocess.run (["swaymsg", "-t", "get_tree", "-r"], capture_output = True)
workspaces.check_returncode ()
workspaces = json.loads (workspaces.stdout.decode ()) ["nodes"]
workspaces = {i ["name"]: sorted ((j ["name"] for j in i ["nodes"]), key = lambda x: x == i ["current_workspace"]) for i in workspaces if i ["name"] != "__i3"}

for i in outputs:
    for j in workspaces [i]:
        _ = subprocess.run (["swaymsg", "workspace", j]).check_returncode ()
        _ = subprocess.run (["grim", "-l", "0", "-o", i, "-"], capture_output = True).check_returncode ()

root = tk.Tk ()
root.withdraw ()
root.update ()
windows = {}
for i in outputs:
    def create_window ():
        windows [i] = tk.Toplevel ()
        windows [i].title (f"_swaymc_{i}")
        windows [i].geometry (f"{outputs [i] [0]}x{outputs [i] [1]}")
        windows [i].resizable (False, False)
        def on_destroy (ev):
            socket.close ()
            context.term ()
            root.quit ()
        windows [i].bind ("<Destroy>", on_destroy)
        windows [i].update_idletasks ()
        root.update_idletasks ()
        time.sleep (0.1)

    while True:
        try:
            subprocess.run (["swaymsg", "focus", "output", i]).check_returncode ()
            create_window ()
            subprocess.run (["swaymsg", "fullscreen", "enable"]).check_returncode ()
            break
        except subprocess.CalledProcessError:
            windows [i].destroy ()
            
    

def switch_desktop ():
    msg = socket.recv ()
    socket.send (b"OK")
    thread = threading.Thread (target = switch_desktop)
    thread.start ()
    print (msg)
    return msg.decode ()
thread = threading.Thread (target = switch_desktop)
thread.start ()

root.mainloop ()