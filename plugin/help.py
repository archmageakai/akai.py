def cmd(author, namespace, send_message):

    helptable = {
        "akaiyen": "https://akai.gikopoi.com/akai.py/akaiyen.html -- or:  akaiyen commands: .convert | .balance | .yen_rate | .gross",
        "game": "https://akai.gikopoi.com/akai.py/game.html -- or:  game commands: .gacha | .gacha_rate | .guarantee | .bag",
    }

    message = namespace.strip()
    msg = message.split()
    output = []
    command = list(helptable.keys())

    if msg[0] == ".help":
        if len(msg) == 1:
            output.append("akai.py web guide: https://akai.gikopoi.com/akai.py/ -- or:  Find commands (type .help <commands>): " + " | ".join(command))
        elif len(msg) > 1 and msg[1] in command:
            output.append(helptable[msg[1]])

    for line in output:
        send_message(line)