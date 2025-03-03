import random

def cmd(author, namespace, send_message):

    message = namespace.strip()
    msg = message.split()
    commands = ["!bloodninja"]
    
    if msg[0] in commands:
        if msg[0] == "!bloodninja":
            quote = get_quote("bloodninja_giko.txt")
            send_message(quote)
#        elif msg[0] == "!command here":
#            output.append(get_quote("txt file here"))

def get_quote(fn):
    with open(f"./quotes/{fn}") as quotedb:
        quotedb = quotedb.read().splitlines()
    return random.choice(quotedb)

print("Quotes plugin loaded")