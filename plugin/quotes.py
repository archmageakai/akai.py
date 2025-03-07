import random

def cmd(author, namespace, send_message):

    message = namespace.strip()
    msg = message.split()
    commands = ["!bloodninja", "!hermit"]
    
    if msg[0] in commands:
        if msg[0] == "!bloodninja":
            quote = get_quote("bloodninja.txt")
            send_message(quote)
        elif msg[0] == "!hermit":
            quote = get_quote("maya.txt")
            send_message(quote)

def get_quote(fn):
    with open(f"./quotes/{fn}") as quotedb:
        quotedb = quotedb.read().splitlines()
    return random.choice(quotedb)

print("Quotes plugin loaded")