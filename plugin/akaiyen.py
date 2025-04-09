import os
import re
import datetime
import time
import math
#import akailogger

# add save states for player/author name

MAX_TRANSFER = 100000
bot_no = None

def set_bot_no(no):
    """Set bot_no from main script."""
    global bot_no
    bot_no = no
    print(f"[yen] sees bot as BOT NO: {bot_no}")

def log_to_file(message):
    """ edit each log_to_file to contain [COMMAND]"""

    """Log messages to the log file."""
    tstamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    format = f"[{tstamp}] {message} \n"

    log_file_path = os.path.expanduser(f"~/akaipy-data/log_akaiyen{bot_no}.txt")
    
    with open(log_file_path, "a") as log_file:
        log_file.write(format)

bankfn = os.path.expanduser("~/akaipy-data/akaiyen.txt")
mula = os.path.expanduser("~/akaipy-data/totalyen.txt")
lotto = os.path.expanduser("~/akaipy-data/lotto.txt")

def send(author, message, send_message):
    """
    Handle messages to detect when a user sends coins to akai.py and process them.
    """
    isThreshold = 0
    
    transaction = False
    akaiyen_total_transfer = 0.00
    
    if author == "giko.py◆BOT":
        match = re.match(r"^(.+) sent akai\.py◆NEET (\d+) gikocoins$", message)
        if match:
            author = match.group(1)
            coins = int(match.group(2))
            print(f"[AKAIYEN] Detected {author} has sent akai.py◆NEET {coins} gikocoins.")

            if coins > MAX_TRANSFER:
                send_message(f"!send {coins} {author}")
                send_message(
                    f"Here is a refund, {author}! We only accept a maximum transfer of {MAX_TRANSFER} gikocoins at this time."
                )
                print(f"[AKAIYEN] for {author}, refund {coins} gikocoins due to over max transfers")
                
                log_to_file(f"!send {coins} {author}")
                log_to_file(
                    f"Here is a refund, {author}! We only accept a maximum transfer of {MAX_TRANSFER} gikocoins at this time.")
            else:
                # start threshold loop               
                rate, threshold, yentotal = akaiyen_rate(author)
                until_threshold = abs(yentotal - threshold)
                until_threshold *= rate

                while coins > until_threshold:
                    chunk_size = 10000
                    num_chunks = until_threshold // chunk_size
                    remaining_threshold = until_threshold % chunk_size

                    print(f"[AKAIYEN] init_above_threshold"
                          f"start chunk processing, {num_chunks} chunks of {chunk_size} and {remaining_threshold} remaining coins")

                    for _ in range(int(num_chunks)):
                        akaiyen = 0.00
                        rate, _, _ = akaiyen_rate(author)
                        akaiyen_i = chunk_size / rate
                        akaiyen += akaiyen_i
                        akaiyen_total_transfer += akaiyen_i
                        write_to_file(author, akaiyen)  
                        write_to_totalyen(author, akaiyen)

                    if remaining_threshold > 0:
                        akaiyen = 0.00
                        rate, _, _ = akaiyen_rate(author)
                        akaiyen_i = remaining_threshold / rate
                        akaiyen += akaiyen_i
                        akaiyen_total_transfer += akaiyen_i
                        write_to_file(author, akaiyen)  
                        write_to_totalyen(author, akaiyen)

                    coins -= until_threshold
                    print(f"coins: {coins}")
                    rate, threshold, yentotal = akaiyen_rate(author)
                    until_threshold = abs(yentotal - threshold)
                    print(until_threshold)
                    until_threshold *= rate
                    print(until_threshold)
                    
                    isThreshold = 1
                    print(f"[AKAIYEN] pass threshold success")
                
                if isThreshold == 1:
                    print(f"[AKAIYEN] until threshold chunk loop finished")
                 # end threshold loop
                
                chunk_size = 10000
                num_chunks = coins // chunk_size
                remaining_coins = coins % chunk_size
                
                print(f"[AKAIYEN] start chunk processing, {num_chunks} chunks of {chunk_size} and {remaining_coins} remaining coins")
                
                # Process in chunks
                for _ in range(int(num_chunks)):
                    akaiyen = 0.00
                    rate, _, _ = akaiyen_rate(author)
                    akaiyen_i = chunk_size / rate
                    akaiyen += akaiyen_i
                    akaiyen_total_transfer += akaiyen_i
                    write_to_file(author, akaiyen)  
                    write_to_totalyen(author, akaiyen)
                
                # remaining coins, outside chunk
                if remaining_coins > 0:
                    akaiyen = 0.00
                    rate, _, _ = akaiyen_rate(author)
                    akaiyen_i = remaining_coins / rate
                    akaiyen += akaiyen_i
                    akaiyen_total_transfer += akaiyen_i
                    write_to_file(author, akaiyen)  
                    write_to_totalyen(author, akaiyen)
                
                print(f"[AKAIYEN] chunk loop finished")
                transaction = True
                
            if transaction == True:
                if akaiyen_total_transfer < 0.01:
                    # Handle case where no akaiyen could be converted
                    send_message(f"!send {coins} {author}")
                    send_message(
                    f"Here is a refund, {author}! Please send enough gikocoins to convert to at least 0.01 akaiyen."
                    )
                    print(f"[AKAIYEN] for {author}, refund {coins} gikocoins, not enough gikocoins to make at least 0.01 akaiyen.")

                    log_to_file(
                    f"Here is a refund, {author}! Please send enough gikocoins to convert to at least 0.01 akaiyen."
                    )
                else:
                    # Send a message to the user with the total converted amount
                    send_message(f"Thank you for your purchase, {author}! You received {akaiyen_total_transfer:.2f} akaiyen.")
                    print(f"[AKAIYEN] {author} received {akaiyen_total_transfer:.2f} akaiyen.")

                    log_to_file(f"Thank you for your purchase, {author}! You received {akaiyen_total_transfer:.2f} akaiyen.")

                    # Get the balance after the purchase
                    balance = check_balance(author)
                    if balance is not None:
                        send_message(f"{author} has a total balance of {balance:.2f} akaiyen.")
                        log_to_file(f"{author} has a total balance of {balance:.2f} akaiyen.")
                    else:
                        send_message(f"An error occurred while checking {author}'s balance.")
                        log_to_file(f"An error occurred while checking {author}'s balance.")

            return {"author": author, "akaiyen": akaiyen_total_transfer}

    return None

def check_balance(author):
    """
    Check the balance of a user from the akaiyen.txt file and return the balance.
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
                            return balance  # Return balance value
                        except ValueError:
                            print(f"[ERROR] Invalid balance format for user {stored_user}: {amount}")
                            return None
                        
        # If the user is not found, return None
        return None
    except FileNotFoundError:
        # Handle the case where the file does not exist
        print(f"[ERROR] No balance file found for check_balance().")
        return None
    except Exception as e:
        # Catch unexpected errors
        print(f"[ERROR] An error occurred while checking balance: {e}")
        return None
        
def check_gross(author):
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
                            return earnings
                        except ValueError:
                            print(f"[ERROR] Invalid format for user {stored_user}: {amount}")
                            return None
        
    except FileNotFoundError:
        # Handle the case where the file does not exist
        print(f"[ERROR] No balance file found for check_total().")
    except Exception as e:
        # Catch unexpected errors
        print(f"[ERROR] An error occurred while checking balance: {e}")

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
    MAX_THRESHOLD = 100000  # cap

    while yentotal >= threshold and threshold <= MAX_THRESHOLD:
        rate *= 10  # Increase the rate by a factor of 10
        threshold *= 10  # Increase the threshold by a factor of 10

    return rate, threshold, yentotal

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

def lottery(added_value):
    """
    akai's lottery, to be used in the future
    """
    lotto_file = os.path.expanduser("~/akaipy-data/lotto.txt")
    
    try:
        # check file
        if os.path.exists(lotto_file) and os.path.getsize(lotto_file) > 0:
            with open(lotto_file, "r") as file:
                current_value = float(file.read().strip()) # read value
        else:
            current_value = 0.0  # Initialize to 0 if file is empty or doesn't exist

        updated_value = current_value + added_value

        with open(lotto_file, "w") as file:
            file.write(f"{updated_value}\n")
    
    except Exception as e:
        print(f"Error: {e}")

""" COMMANDS """

command = {
                ".convert",
                ".balance",
                ".yen_rate",
                ".gross"
                        }

def cmd(author, namespace, send_message):
    
    message = namespace.strip()
    result = None

    if author and message:
        result = send(author, message, send_message)

    # HOW TO CONVERT GIKOCOINS TO AKAIYEN
    if message == ".convert":
        send_message(f"Type '!send <amount> akai.py◆NEET' to convert gikocoins to akaiyen. "
                     f"(max transfer: {MAX_TRANSFER} gikocoins, and you will be refunded upon transactions beyond maximum)")
        log_to_file(f"Type '!send <amount> akai.py◆NEET' to convert gikocoins to akaiyen. "
                     f"(max transfer: {MAX_TRANSFER} gikocoins, and you will be refunded upon transactions beyond maximum)")

    # CHECK BALANCE
    if message == ".balance":
        balance = check_balance(author)
        if balance is not None:
            send_message(f"{author} has a balance of {balance:.2f} akaiyen.")
            log_to_file(f"{author} has a balance of {balance:.2f} akaiyen.")
        else:
            send_message(f"{author} does not have any akaiyen!")
            log_to_file(f"{author} does not have any akaiyen!")

    # CHECK RATE
    if message == ".yen_rate":
        rate, _, _ = akaiyen_rate(author)
        send_message(f"{author}: your rate is 1 akaiyen = {rate} gikocoins [ see more info: https://akai.gikopoi.com/akai.py/rate.html ]")
        log_to_file(f"{author}: your rate is 1 akaiyen = {rate} gikocoins [ see more info: https://akai.gikopoi.com/akai.py/rate.html ]")
    
    # CHECK GROSS
    if message == ".gross":
        earnings = check_gross(author)
        if earnings is not None:
            send_message(f"{author} has a gross earnings of {earnings:.2f} akaiyen.")
            log_to_file(f"{author} has a gross earnings of {earnings:.2f} akaiyen.")
        else:
            send_message(f"{author} has no gross earnings.")
            log_to_file(f"{author} has no gross earnings.")