import os
import re
import time
import math

bankfn = os.path.expanduser("~/akaipy-data/akaiyen.txt")
mula = os.path.expanduser("~/akaipy-data/totalyen.txt")

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

            rate = akaiyen_rate(author)  # Get the rate for 1 akaiyen

            # Convert gikocoins to akaiyen (allowing decimal conversion)
            akaiyen = math.floor((coins / rate) * 100) / 100  #always result with 2 decimals, rounded down
            print(f"[AKAIYEN] {coins} gikocoins is equivalent to {akaiyen} akaiyen.")
            if akaiyen == 0.00:
                # in case of akaiyen amount being zero
                send_message(f"!send {coins} {author}")
                send_message(
                    f"Here is a refund, {author}! Please send enough gikocoins to convert to at least 0.01 akaiyen. (1 akaiyen = {rate} gikocoins.)"
                )
            else:
                # Write to file with the new akaiyen amount
                write_to_file(author, akaiyen)
                write_to_totalyen(author, akaiyen)

                # Send a message to the user with the converted amount
                send_message(f"Thank you for your donation, {author}! You received {akaiyen:.2f} akaiyen.")

                # Check the balance after donation
                check_balance(author, send_message)

            return {"author": author, "akaiyen": akaiyen}

    return None

def check_balance(author, send_message):
    """
    Check the balance of a user from the akaiyen.txt file and send a message with the balance.
    Handles usernames with spaces, special characters, and other non-standard formats.
    Performs case-sensitive matching for the username.
    """
    try:
        with open(bankfn, "r") as f:
            for line in f:
                # Split the line into username and amount, assuming the amount is the last part
                parts = line.rsplit(maxsplit=1)
                if len(parts) == 2:
                    stored_user, amount = parts
                    # Match the username exactly (case-sensitive)
                    if stored_user.strip() == author.strip():
                        try:
                            balance = float(amount)  # Ensure the amount is a valid number
                            send_message(f"{author} has a total balance of {balance:.2f} akaiyen.")
                            return
                        except ValueError:
                            print(f"[ERROR] Invalid balance format for user {stored_user}: {amount}")
                            send_message(f"An error occurred while checking {author}'s balance.")
                            return

        # If the user is not found
        send_message(f"{author} has no akaiyen balance.")
    except FileNotFoundError:
        # Handle the case where the file does not exist
        send_message(f"No balance file found. {author} has no akaiyen balance.")
    except Exception as e:
        # Catch unexpected errors
        print(f"[ERROR] An error occurred while checking balance: {e}")
        send_message(f"An error occurred while checking {author}'s balance.")

    
        # If the user is not found
        send_message(f"{author} has no akaiyen balance.")
    except FileNotFoundError:
        # Handle the case where the file does not exist
        send_message(f"No balance file found. {author} has no akaiyen balance.")
    except Exception as e:
        # Catch unexpected errors
        print(f"[ERROR] An error occurred while checking balance: {e}")
        send_message(f"An error occurred while checking {author}'s balance.")

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


def akaiyen_rate(author):
    """
    Calculate the rate of 1 akaiyen based on the total akaiyen in user wallet.
    """
    yentotal = 0  # Initialize yentotal to a default value

    try:
        with open(mula, "r") as f:
            for line in f:
                # Split the line into username and amount, assuming the amount is the last part
                parts = line.rsplit(maxsplit=1)
                if len(parts) == 2:
                    stored_user, amount = parts
                    # Match the username exactly (case-sensitive)
                    if stored_user.strip() == author.strip():
                        try:
                            yentotal = float(amount)  # Ensure the amount is a valid number
                            break  # Exit the loop once the user is found
                        except ValueError:
                            print(f"[ERROR] Invalid balance format for user {stored_user}: {amount}")
                            return None
    except FileNotFoundError:
        print(f"[ERROR] The file {mula} was not found.")
        return None
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        return None

    # This part is outside the try block
    if yentotal == 0:
        rate = 10
        print("1 akaiyen = {rate} gikocoin")
    else:
        rate = yentotal * 10.00
        rate = round(rate)  # Round to the nearest integer
        print(f"1 akaiyen = {rate} gikocoins.")

    return rate

def write_to_file(author, akaiyen):
    """
    Writes to akaiyen.txt
    """
    
    os.makedirs(os.path.dirname(bankfn), exist_ok=True)

    print(f"[AKAIYEN] Writing to file {bankfn}...")

    records = {}
    if os.path.exists(bankfn):
        print(f"[AKAIYEN] File {bankfn} found, reading...")
        with open(bankfn, "r") as f:
            for line in f:
                # Use rsplit(maxsplit=1) to handle spaces in the username
                parts = line.rsplit(maxsplit=1)
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
                f.write(f"{user} {amount:.2f}\n")  # Store as float with 2 decimal places
        print(f"[AKAIYEN] Updated {bankfn}: {author} now has {records[author]:.2f} akaiyen.")
    except Exception as e:
        print(f"[AKAIYEN] Error writing to file: {e}")
        
def write_to_totalyen(author, akaiyen):
    """
    Writes to totalyen.txt
    """
    
    os.makedirs(os.path.dirname(mula), exist_ok=True)

    print(f"[AKAIYEN] Writing to file {mula}...")

    records = {}
    if os.path.exists(mula):
        print(f"[AKAIYEN] File {mula} found, reading...")
        with open(mula, "r") as f:
            for line in f:
                # Use rsplit(maxsplit=1) to handle spaces in the username
                parts = line.rsplit(maxsplit=1)
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
        with open(mula, "w") as f:
            for user, amount in records.items():
                f.write(f"{user} {amount:.2f}\n")  # Store as float with 2 decimal places
        print(f"[AKAIYEN] Updated {mula}: {author} now has {records[author]:.2f} akaiyen.")
    except Exception as e:
        print(f"[AKAIYEN] Error writing to file: {e}")

def monitor(author, namespace, send_message):
    """
    Monitor incoming messages and act on specific patterns.
    """
    message = namespace
    result = None

    if author and message:
        result = send(author, message, send_message)

    # HELP
    if message == ".help":
        send_message(f"Convert gikocoins to akaiyen using !send <amount> akai.py◆NEET")
        send_message(f"'Commands': .akai | .akaiyen | .akaiyen_rate")

    # akai
    if message == ".akai":
        send_message(f"https://akai.gikopoi.com")

    # CHECK BALANCE
    if message == ".akaiyen":
        check_balance(author, send_message)

    # CHECK RATE
    if message == ".akaiyen_rate":
        rate = akaiyen_rate(author)  # Corrected function call
        if rate is not None:
            if rate == 0.10:
                send_message(f"{author}: your rate is 1 akaiyen = {rate} gikocoins")
            else:
                send_message(f"{author}: your rate is 1 akaiyen = {rate} gikocoins")