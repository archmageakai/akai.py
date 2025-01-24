import os
import re
import time
import math

bankfn = os.path.expanduser("./data/akaiyen.txt")

def send(author, message, send_message):
    """
    Handle messages to detect when a user sends coins to akai.py and process them.
    """

    if author == "giko.py◆BOT":
        match = re.match(r"^(.+) sent akai\.py◆NEET (\d+) gikocoins$", message)
        if match:
            author = match.group(1)
            coins = int(match.group(2))
            print(f"[AKAIYEN] Detected {author} has sent akai.py◆NEET {coins} gikocoins.")

            # Get the total coins by calling sum_all
            total = sum_all()  # Get the total coins from the file

            # Calculate the rate of 1 akaiyen based on the total coins
            rate = akaiyen_rate(total)  # Get the rate for 1 akaiyen

            # Convert gikocoins to akaiyen (allowing decimal conversion)
            akaiyen = coins / rate  # Use the rate to convert gikocoins to akaiyen
            print(f"[AKAIYEN] {coins} gikocoins is equivalent to {akaiyen} akaiyen.")

            # Write to file with the new akaiyen amount (allowing decimals)
            write_to_file(author, akaiyen)

            # Send a message to the user with the converted amount
            send_message(f"Thank you for your donation, {author}! You received {akaiyen:.2f} akaiyen.")

            # Check the balance after donation
            check_balance(author, send_message)

            return {"author": author, "akaiyen": akaiyen}

    return None


def check_balance(author, send_message):
    """
    Check the balance of a user from the akaiyen.txt file and send a message with the balance.
    """

    # Read the file and find the user
    with open(bankfn, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                stored_user, amount = parts
                if stored_user == author:
                    send_message(f"{author} has a total balance of {amount} akaiyen.")
                    return
    
    # If the user is not found
    send_message(f"{author} has no akaiyen balance.")


def sum_all():
    """
    Sum up all the coin amounts (second part of each line) in the akaiyen.txt file.
    """
    total = 0.0  # Initialize as float to allow decimal summation

    # Read the file and sum the coin amounts
    with open(bankfn, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                try:
                    akaiyen = float(parts[1])  # Allow decimals here
                    total += akaiyen
                except ValueError:
                    print(f"Invalid coin value on line: {line.strip()}")
    
    print(f"Total coins in {bankfn}: {total}")
    return total


def akaiyen_rate(total):
    """
    Calculate the rate of 1 akaiyen based on the total coins.
    """
    if total == 0:
        print("1 akaiyen = 1 gikocoin")
        rate = 1
        return rate
    rate = total * 10.00
    print(f"1 akaiyen = {rate} gikocoins.")
    return rate


def write_to_file(author, akaiyen):
    """
    Write the user's name and coin amount to the file, or update if the user exists.
    """
    
    os.makedirs(os.path.dirname(bankfn), exist_ok=True)

    print(f"[AKAIYEN] Writing to file {bankfn}...")

    records = {}
    if os.path.exists(bankfn):
        print(f"[AKAIYEN] File {bankfn} found, reading...")
        with open(bankfn, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    user, amount = parts
                    try:
                        records[user] = float(amount)  # Allow decimals here
                    except ValueError:
                        print(f"Invalid amount for {user}: {amount}")
                        continue

    # Update the user's record
    if author in records:
        records[author] += akaiyen  # Add the new coins to the existing amount
        print(f"[AKAIYEN] {author} already exists. Adding {akaiyen} akaiyen.")
    else:
        records[author] = akaiyen  # Add a new record for the user
        print(f"[AKAIYEN] {author} not found. Adding new record with {akaiyen} akaiyen.")

    # Write the updated records back to the file
    try:
        with open(bankfn, "w") as f:
            for user, amount in records.items():
                f.write(f"{user} {amount:.2f}\n")  # Store as float with 6 decimal places
        print(f"[AKAIYEN] Updated {bankfn}: {author} now has {records[author]:.2f} akaiyen.")
    except Exception as e:
        print(f"[AKAIYEN] Error writing to file: {e}")

def monitor(author, namespace, send_message):
    """
    Monitor incoming messages and act on specific patterns.
    """
    
    #TRANSFER FROM GIKOCOINS TO AKAIYEN
    message = namespace
    
    result = None

    if author and message:
        result = send(author, message, send_message)
    
    #HELP
    if message == ".help":
        send_message(f"Convert gikocoins to akaiyen using !send <amount> akai.py◆NEET")
        send_message(f"'Commands': .akai | .akaiyen | .akaiyen_rate")
        
    #akai
    if message == ".akai":
        send_message(f"https://akai.gikopoi.com")
    
    #CHECK BALANCE
    if message == ".akaiyen":
        check_balance(author, send_message)

    #CHECK RATE
    if message == ".akaiyen_rate":
        total = sum_all()
        rate = akaiyen_rate(total)
        disprate = math.floor(rate)
        send_message(f"1 akaiyen = {disprate} gikocoins.")