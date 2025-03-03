import datetime
import time
import socketio
import requests
import sys
import os

from plugin import help
from plugin import quotes
from plugin import transform
from plugin import reset
from plugin import akaiyen
# from plugin import gacha

sio = socketio.Client()
session = requests.Session()

Users = {}
my_id = ""
pid = ""
api = ""
anon_name = "Spy"
anti_spy = False
ircmode = False
ircroom = "null"
tripcode = True

if tripcode is True:
    with open(os.path.expanduser("~/tripcode.txt"), "r") as trip:
        trip = trip.read().splitlines()[0].strip()

# Initialize seen as a dictionary
seen = {}

# Log
filename = input("Enter the name for the log file (default: log.txt): ").strip()
if not filename:
    filename = "log"    
log_file_path = os.path.expanduser(f"~/{filename}.txt")
log_file = open(log_file_path, "a")
print(f"Log file: {log_file_path}")

def log_to_file(message):
    """Log messages to the log file."""
    log_file.write(message + "\n")
    log_file.flush()

def upd_seen(username):
    """Update seen dictionary with the current timestamp."""
    seen[username] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    print("[*] Starting reset thread...")
    reset.start()
    print("[*] Reset thread started!")

    global api
    server = "play.gikopoi.com"
    area = "for"
    room = "bar"
    character = input("Enter your giko (default: akai): ")
    if not character:
        character = "akai"
    name = "akai.py"
    password = "VIPQUALITY"
    if tripcode:
        name = name + "#" + trip


    if len(sys.argv) > 1:
        print(sys.argv)
        room = sys.argv[1]

    if room == ircroom:
        global ircmode
        ircmode = True

        global ircrelay
        from plugin import ircrelay

        global plugins
        plugins.append("ircrelay")

        import threading
        x = threading.Thread(target=get_irc_msgs)
        x.start()

    if "poipoi" in server:
        api = "/api"

    logon(server, area, room, character, name, password)

    print([Users[u] for u in Users])

    while True:
        val = input()  # Read input from the user
        if len(val):
            tstamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_to_file(f"{tstamp} < {get_username(my_id)} > {val}")  # Log the input
            if val[0] == ",":
                move_around(val[1:])
            else:
                sio.emit("user-msg", val)
        else:
            sio.emit("user-msg", val)
        pass

    return
    

def logon(server, area, room, character, name, password):
    global my_id
    global pid

    url = "https://" + server
    wss = "ws://" + server + ":8085/socket.io/"
    print("[*] Connect")
    log_to_file("[*] Connecting to server")
    connect_value = {"userName": name,
                     "characterId": character,
                     "areaId": area,
                     "roomId": room,
                     "password": password}
    connect_response = session.post(f"{url}{api}/login", connect_value)
    connect_json = connect_response.json()
    if not connect_json['isLoginSuccessful'] is True:
        print("Not able to login")
        log_to_file("[!] Login failed")
        return

    print("[*] Connected")
    log_to_file("[*] Successfully connected")
    user_id = str(connect_json['userId'])
    pid = str(connect_json['privateUserId'])
    version = str(connect_json["appVersion"])
    
    t_form = "%Y-%m-%d %H:%M:%S"
    timestamp = datetime.datetime.now().strftime(t_form)
    send = " ".join([timestamp, user_id,
                     "window.EXPECTED_SERVER_VERSION:", version,
                     "loginMessage.appVersion:", version,
                     "DIFFERENT: false"])
    ret = session.post(f"{url}/client-log",
                       data=send,
                       headers={"Content-Type": "text/plain"})
    
    my_id = user_id
    print(f"id: {user_id}")
    log_to_file(f"id: {user_id}")
    sio.connect(wss, headers={"private-user-id": pid})
    get_users(session, url, area, room)
    return

def get_users(s: requests.Session, server, area, room):
    print("[*] Get Rooms Users")
    log_to_file("[*] Fetching room users")
    val = s.get(f'{server}{api}/areas/{area}/rooms/{room}',
                headers={"Authentication": f"Bearer {pid}"})
    if val.status_code == 200:
        users = val.json()['connectedUsers']
        print("[*] found {}".format(str(len(users))))
        log_to_file("[*] Found {} users".format(str(len(users))))
        for user in users:
            global Users
            Users[user['id']] = user['name']
            if len(user['name']) == 0:
                Users[user['id']] = anon_name
            if len(Users[user['id']].strip()):
                upd_seen(Users[user['id']])  # Update seen dictionary
        # Log the list of users
        log_to_file("[" + ", ".join([Users[u] for u in Users]) + "]")

def get_username(userid):
    try:
        return Users[userid]
    except:
        return anon_name

def send_message(msg):
    """Send a message and log it."""
    # Send the message
    sio.emit("user-msg", msg)
    sio.emit("user-msg", "")
    
    # Log the message
    tstamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_to_file(f"{tstamp} < {get_username(my_id)} > {msg}")

def move_around(directions):
    uplr = {"u": "up", "d": "down", "l": "left", "r": "right"}
    directions = list(directions)
    for d in directions:
        if d in uplr:
            sio.emit("user-move", uplr[d])

@sio.event
def connect():
    print("[*] I'm connected!")
    log_to_file("[*] Connected to socket")

@sio.event
def connect_error(data):
    print("[*] The connection failed!")
    log_to_file("[!] Socket connection failed")

@sio.event
def disconnect():
    print("I'm disconnected!")
    log_to_file("[!] Disconnected from socket")

@sio.on('server-user-joined-room')
def user_join(data):
    try:
        global Users
        user = [data['id'], data['name']]
        if data['id'] == my_id:
            return
        if len(data['name']) == 0:
            user[1] = anon_name
            if anti_spy:
                send_message("Go to hell Spy")
        Users[user[0]] = user[1]
        tstamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(tstamp, "{} joined".format(user[1]))
        log_to_file(f"{tstamp}: {user[1]} joined")
        if len(user[1].strip()):
            upd_seen(user[1])
    except Exception as ex:
        print(ex)
        log_to_file(f"[!] Error in user_join: {ex}")
        pass
    # Log the updated Users list
    user_list = ", ".join([Users[u] for u in Users])
    print("[+] " + str([Users[u] for u in Users]))
    log_to_file("[+] " + "[" + user_list + "]")


@sio.on('server-user-left-room')
def user_leave(data):
    try:
        global Users
        tstamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(tstamp, "{} left".format(Users[data]))
        log_to_file(f"{tstamp}: {Users[data]} left")
        if len(Users[data].strip()):
            upd_seen(Users[data])        
        del Users[data]
    except Exception as ex:
        print(ex)
        log_to_file(f"[!] Error in user_leave: {ex}")
        pass
    # Log the updated Users list
    user_list = ", ".join([Users[u] for u in Users])
    print("[-] " + str([Users[u] for u in Users]))
    log_to_file("[-] " + "[" + user_list + "]")

@sio.on('server-msg')
def server_msg(event, namespace):
    author = get_username(event)
    output = []

    if author == "":
        author = anon_name
    if event == my_id:
        return
    if len(namespace) == 0:
        return
    
    tstamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = '{} < {} > {}'.format(tstamp, author, namespace)
    print(msg)
    log_to_file(msg)
    
    # help.py
    help.cmd(author, namespace, send_message)

    # quotes
    quotes.cmd(author, namespace, send_message)

    # transform
    transform.cmd(author, namespace, send_message)
    
    # akaiyen.py
    akaiyen.cmd(author, namespace, send_message)

    # gacha.py
    # gacha.cmd(author, namespace, send_message) # call gacha

    if (author == anon_name) and anti_spy:
        return

def get_irc_msgs():
    while True:
        if ircrelay.lastread < ircrelay.modified:
            qdmsgs = ircrelay.queued_msgs()
            for m in qdmsgs:
                send_message(m)
                log_to_file(m)
                time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    finally:
        log_file.close()
