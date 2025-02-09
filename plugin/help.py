def cmd(author, namespace, send_message):

    helptable = {
        "akaiyen": "akaiyen commands: .convert | .yen | .rate | .total",
        
    }

    message = namespace.strip()
    msg = message.split()
    output = []
    topics = list(helptable.keys())

    if msg[0] == ".help":
        if len(msg) == 1:
            output.append("[ List of topics | type .help <topic> ]: " + ", ".join(topics))
        elif len(msg) > 1 and msg[1] in topics:
            output.append(helptable[msg[1]])

    for line in output:
        send_message(line)