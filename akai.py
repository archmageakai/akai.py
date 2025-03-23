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
from plugin import gacha

# BOOLEAN
SWITCH_QUOTES = True
SWITCH_TRANSFORM = False
SWITCH_YEN = True
SWITCH_GACHA = True

sio = socketio.Client()
session = requests.Session()

anon_name = "Spy"
Users = {}
my_id = ""
pid = ""
api = ""
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
        character = "gacha"
    name = "akai.py"
    password = "GACHAPON"
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
        val = input()
        if len(val):
            tstamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_to_file(f"{tstamp} < {get_username(my_id)} > {val}")

            switches = {
                ",QUOTES": "SWITCH_QUOTES",
                ",TRANSFORM": "SWITCH_TRANSFORM",
                ",YEN": "SWITCH_YEN",
                ",GACHA": "SWITCH_GACHA"
                        }
            
            if val == ",SWITCH":  
                print(', '.join(f"{key}: {globals()[var_name]}" for key, var_name in switches.items()))

            if val in switches:
                switch_name = switches[val]

                globals()[switches[val]] = not globals()[switches[val]]

                print(f"Flipped {switch_name} to {globals()[switch_name]}")

            # get user
            if val == ",USERS":  
                get_user_ids()

            # get world
            if val == ",WORLD":
                get_world(session, server, area, pid)

            if val == ",WORLDF":
                get_world(session, server, area, pid, is_worldf=True)
            
            # movement
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
    print("[*] Get Rooms Users")
    log_to_file("[*] Fetching room users")
    get_users(session, url, area, room)
    return

"""
def set_user_status(user, add_idle=False):
    is_afk = user.get("isInactive", False)
    idle = "💤" if is_afk else ""
    
    user_name = user.get('name', anon_name).strip()
    
    if not user_name:
        user_name = anon_name
    
    if add_idle:
        user['name'] = f"{idle}{user_name}"
    else:
        user['name'] = f"{user_name}"
"""

def get_users(s: requests.Session, server, area, room):
    val = s.get(f'{server}{api}/areas/{area}/rooms/{room}', headers={"Authentication": f"Bearer {pid}"})
    
    if val.status_code == 200:
        users = val.json().get('connectedUsers', [])
        print("[*] found {} users".format(len(users)))
        log_to_file("[*] Found {} users".format(len(users)))
        
        for user in users:
            global Users
            user_id = user['id']
            
            #set_user_status(user, add_idle=True)

            Users[user_id] = user['name']
            upd_seen(user['name'])

        user_list = ", ".join([Users[u] for u in Users])
        log_to_file("[+] " + "[" + user_list + "]")

def get_user_ids():
    global Users
    print("[*] Get user/ID initialized")

    if not Users:
        print("[*] No users found in the Users dictionary.")
        return

    for user_id, username in Users.items():
        print(f"- {username} ({user_id})")

def get_world(s: requests.Session, server, area, pid, is_worldf=False):
    print("[*] Fetching world users...")

    if not server.startswith("http"):
        server = f"https://{server}"

    with open('./roomid.txt', 'r') as file:
        room_names = [line.strip() for line in file.readlines()]

    for room_name in room_names:
        url = f'{server}{api}/areas/{area}/rooms/{room_name}'

        response = s.get(url, headers={"Authentication": f"Bearer {pid}"})

        if response.status_code == 200:
            room_data = response.json()
            users = room_data.get('connectedUsers', [])

            for user in users:
                if not user['name'].strip():
                    user['name'] = anon_name

                #set_user_status(user, add_idle=True)

            if users:
                print(f"[*] Found {len(users)} users in {room_name}.")
                if is_worldf:
                    print(f"[*] Users in {room_name}:")
                    for user_id, username in [(user['id'], user['name']) for user in users]:
                        print(f"- {username} ({user_id})")
                else:
                    user_list = ", ".join([f"'{user['name']}'" for user in users])
                    print(f"- Users in {room_name}: [{user_list}]")
                
        else:
            print(f"[!] Error: Could not fetch data for room {room_name}. Status Code: {response.status_code}")

    print(f"[*] WORLD USERS GATHER COMPLETE.")

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
        printJoin = f"{tstamp} {user[1]} joined (ID: {user[0]})"
        print(printJoin)
        log_to_file(printJoin)
        if len(user[1].strip()):
            upd_seen(user[1])
    except Exception as ex:
        #error_message = f"{tstamp} * Error in user_join: {ex} [{Users[data]}]"
        #print(error_message)
        #log_to_file(error_message)
        print(ex)
        log_to_file(f"[!] Error in user_join: {ex}")
        pass
    user_list = ", ".join([Users[u] for u in Users])
    print("[+] " + str([Users[u] for u in Users]))
    log_to_file("[+] " + "[" + user_list + "]")


@sio.on('server-user-left-room')
def user_leave(data):
    try:
        global Users
        tstamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        printLeave = f"{tstamp} {Users[data]} left (ID: {data})"
        print(printLeave)
        log_to_file(printLeave)
        if len(Users[data].strip()):
            upd_seen(Users[data])        
        del Users[data]
    except Exception as ex:
        #error_message = f"{tstamp} * Error in user_leave: {ex} [{Users[data]}]"
        #print(error_message)
        #log_to_file(error_message)
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

    # remotely turn off plugins
    remote_switch(author, namespace, send_message)

    # help.py
    help.cmd(author, namespace, send_message)

    # quotes
    if SWITCH_QUOTES == True:
        quotes.cmd(author, namespace, send_message)

    # transform
    if SWITCH_TRANSFORM == True:
        transform.cmd(author, namespace, send_message)
    
    # akaiyen.py
    if SWITCH_YEN == True:
        akaiyen.cmd(author, namespace, send_message)

    # gacha.py
    if SWITCH_GACHA == True:
        gacha.cmd(author, namespace, send_message) # call gacha

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

def remote_switch(author, namespace, send_message):
    global SWITCH_YEN
    global SWITCH_GACHA
    message = namespace.strip()
    msg = message.split()

    auth = ["Akai◆giko//JRnk", "Archduke◆cRwJk8JEBs"]
    commands = [",YEN", ",GACHA"]

    if author in auth:
        # Handle authorized users
        if msg[0] == ",YEN":  # Check for ",YEN"
            SWITCH_YEN = not SWITCH_YEN
            print(f"SWITCH_YEN is now {'ON' if SWITCH_YEN else 'OFF'}")
        elif msg[0] == ",GACHA":  # Check for ",GACHA"
            SWITCH_GACHA = not SWITCH_GACHA
            print(f"SWITCH_GACHA is now {'ON' if SWITCH_GACHA else 'OFF'}")
    else:
        # Handle unauthorized users
        not_authorized = (
            "01010000 01001100 01000101 01000001 01010011 01000101 "
            "00100000 "
            "01000100 01001001 01010011 01010011 01000101 01000111 01000001 01010010 01000100 "
            "00100000 "
            "01010100 01001000 01000001 01010100 "
            "00100000 "
            "01001001 "
            "00100000 "
            "01010011 01010101 01000011 01001011 "
            "00100000 "
            "01000011 01001111 01000011 01001011 01010011"
        )
        
        ascii_error = transform.bin_to_ascii(not_authorized)
        send_message(f"{author} shouts to the world, \"{ascii_error}!\"")

    # Return the updated switches if needed
    return SWITCH_YEN, SWITCH_GACHA


if __name__ == "__main__":
    try:
        main()
    finally:
        log_file.close()
