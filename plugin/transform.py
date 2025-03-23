import random

def bin_to_ascii(binary_string):
    binary_values = binary_string.split()
    ascii_text = ''.join(chr(int(b, 2)) for b in binary_values)
    return ascii_text

def randompull(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return random.choice(lines).strip()

filename = "./misc/binary.txt"

def cmd(author, namespace, send_message):

    message = namespace.strip()
    msg = message.split()
    commands = [".transform", ".plan9", ".henshin"]
    user_list = ["Akai◆giko//JRnk", 
                 "meow◆meow/DrxXk", 
                 "Archduke◆cRwJk8JEBs", 
                 "gyudon_addict◆hawaiiZtQ6"]
    
    if msg[0] in commands:
        if author in user_list:
            if msg[0] == ".transform":
                random_binary = randompull(filename)
                ascii_output = bin_to_ascii(random_binary)
                send_message(ascii_output)
            elif msg[0] == ".plan9":
                    send_message("#gnot")
            elif msg[0] == ".henshin":
                    send_message("#henshin")
        elif author not in user_list:
            # DISREGARD MSG
            not_authorized = (
    "01010000 01001100 01000101 01000001 01010011 01000101 "
    "00100000 "
    "01000100 01001001 01010011 01010010 01000101 01000111 01000001 01010010 01000100 "
    "00100000 "
    "01010100 01001000 01000001 01010100 "
    "00100000 "
    "01001001 "
    "00100000 "
    "01010011 01010101 01000011 01001011 "
    "00100000 "
    "01000011 01001111 01000011 01001011 01010011"
    
            )

            ascii_error = bin_to_ascii(not_authorized)
            send_message(f"#spy {author} shouts to the world, \"{ascii_error}!\"")