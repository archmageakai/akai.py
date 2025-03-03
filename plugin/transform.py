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
    commands = [".transform"]
    user_list = ["Akai◆giko//JRnk", 
                 "meow◆meow/DrxXk", 
                 "Archduke◆cRwJk8JEBs", 
                 "gyudon_addict◆hawaiiZtQ6"]
    
    if msg[0] in commands:
        if msg[0] == ".transform":
            if author in user_list:
                random_binary = randompull(filename)
                ascii_output = bin_to_ascii(random_binary)
                send_message(ascii_output)