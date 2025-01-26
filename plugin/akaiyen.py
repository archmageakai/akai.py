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
    
    transaction = False
    akaiyen_total_transfer = 0.00
    
    if author == "giko.py◆BOT":
        match = re.match(r"^(.+) sent akai\.py◆NEET (\d+) gikocoins$", message)
        if match:
            author = match.group(1)
            coins = int(match.group(2))
            print(f"[AKAIYEN] Detected {author} has sent akai.py◆NEET {coins} gikocoins.")

            if coins > 10000:
                send_message(f"!send {coins} {author}")
                send_message(
                    f"Here is a refund, {author}! We only accept a maximum transfer of 10000 gikocoins at this time."
                )
                print(f"[AKAIYEN] for {author}, refund {coins} gikocoins due to over max transfers")
            else:               
                # Process each gikocoin individually      
                print(f"[AKAIYEN] start loop - reading coins/rates, writing to bank/records")
                for _ in range(coins):
                    akaiyen = 0.00
                    rate = akaiyen_rate(author)
                    akaiyen_i = 1 / rate
                    akaiyen += akaiyen_i
                    akaiyen_total_transfer += akaiyen_i
                    write_to_file(author, akaiyen)  
                    write_to_totalyen(author, akaiyen)
                print(f"[AKAIYEN] loop finished")
                transaction = True
                
            if transaction == True:
                if akaiyen_total_transfer == 0.00:
                    # Handle case where no akaiyen could be converted
                    send_message(f"!send {coins} {author}")
                    send_message(
                    f"Here is a refund, {author}! Please send enough gikocoins to convert to at least 0.01 akaiyen."
                    )
                    print(f"[AKAIYEN] for {author}, refund {coins} gikocoins, not enough gikocoins to make at least 0.01 akaiyen.")
                else:
                    # Send a message to the user with the total converted amount
                    send_message(f"Thank you for your purchase, {author}! You received {akaiyen_total_transfer:.2f} akaiyen.")
                    print(f"[AKAIYEN] {author} received {akaiyen_total_transfer:.2f} akaiyen.")

                    # Check the balance after the purchase
                    check_balance(author, send_message)

            return {"author": author, "akaiyen": akaiyen_total_transfer}

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
        
def check_total(author, send_message):
    """
    Check the earnings of a user from the totalyen.txt file and send a message with the total earnings.
    Handles usernames with spaces, special characters, and other non-standard formats.
    Performs case-sensitive matching for the username.
    """
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
                            earnings = float(amount)  # Ensure the amount is a valid number
                            send_message(f"{author} has a total earnings of {earnings:.2f} akaiyen.")
                            return
                        except ValueError:
                            print(f"[ERROR] Invalid format for user {stored_user}: {amount}")
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

def akaiyen_rate(author):
    """
    Calculate the rate of 1 akaiyen based on the total akaiyen in total akaiyen user has ever acquired.
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

    # Determine the rate dynamically
    rate = 10  # Start with the base rate
    threshold = 100  # Initial threshold

    while yentotal >= threshold:
        rate *= 10  # Increase the rate by a factor of 10
        threshold *= 10  # Increase the threshold by a factor of 10

    return rate

def write_to_file(author, akaiyen):
    """
    Writes to akaiyen.txt
    """
    
    os.makedirs(os.path.dirname(bankfn), exist_ok=True)

    records = {}
    if os.path.exists(bankfn):
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
    else:
        records[author] = akaiyen  # Add a new record for the user

    # Write the updated records back to the file
    try:
        with open(bankfn, "w") as f:
            for user, amount in records.items():
                f.write(f"{user} {amount:.2f}\n")  # Store as float with 2 decimal places
    except Exception as e:
        print(f"[AKAIYEN] Error writing to file: {e}")
        
def write_to_totalyen(author, akaiyen):
    """
    Writes to totalyen.txt
    """
    
    os.makedirs(os.path.dirname(mula), exist_ok=True)

    records = {}
    if os.path.exists(mula):
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
    else:
        records[author] = akaiyen  # Add a new record for the user

    # Write the updated records back to the file
    try:
        with open(mula, "w") as f:
            for user, amount in records.items():
                f.write(f"{user} {amount:.2f}\n")  # Store as float with 2 decimal places
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
        send_message(f"'Commands': .akai | .yen | .rate | .total")

    # akai
    if message == ".site":
        send_message(f"https://akai.gikopoi.com/akai.py")

    # CHECK BALANCE
    if message == ".yen":
        check_balance(author, send_message)

    # CHECK RATE
    if message == ".rate":
        rate = akaiyen_rate(author)
        send_message(f"{author}: your rate is 1 akaiyen = {rate} gikocoins [ see more info: https://akai.gikopoi.com/akai.py/rate.html ]")
    
    # CHECK TOTAL EARNINGS
    if message == ".total":
        check_total(author, send_message)