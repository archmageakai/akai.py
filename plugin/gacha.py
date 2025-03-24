import random
import time
import json
import os
#import akailogger
from plugin.akaiyen import check_balance, write_to_file, lottery

"""

** change/style output (debug/terminal as well as gikopoi sendmsg) messages
** incl. [BLADE] or [ITEM] at beginning of pulled_item as well as [*-STAR] at end

"""


directory = open(os.path.expanduser("~/akaipy-data/gacha_dir.txt"), "r")
directory = directory.read().splitlines()[0].strip()

# Load
def load_users():
    file_path = os.path.expanduser(f"{directory}/users.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            users_data = json.load(f)
            return users_data["users"]  # Return the users list, not the whole JSON
    return []

def load_items():
    file_path = os.path.expanduser(f"{directory}/items.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)["items"]  # Return the list of items
    return []

def load_blades():
    file_path = os.path.expanduser(f"{directory}/blade.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)["blades"]  # Return the list of blades
    return []

# Save
def save_users(users_data):
    file_path = os.path.expanduser(f"{directory}/users.json")
    with open(file_path, "w") as f:
        json.dump({"users": users_data}, f, indent=4)  # Save to the correct structure

# get create user function
def get_user(author, users_data):
    """
    Get the user data for the specified author. 

    If the user doesn't exist,
    create a new account and add it to user data JSON.
    """
    normalized_author = author.strip().lower()

    # Check if the user exists
    user_data = next((user for user in users_data if user["player_name"].strip().lower() == normalized_author), None)
    
    if user_data is None:
        # If the user doesn't exist, create a new user
        user_data = {
            "player_name": author,
            "currencies": {
                "yen": 0,
                "gross_yen": 0
            },
            "gacha": {
                "today": 0,
                "guarantee": 0,
                "total": 0
            },
            "items": {},
            "blades": {
                "5.0": {
                    "core_slots": {
                        "available": 7,
                        "used": 0,
                        "broken": 0
                    }
                }
            }
        }
        
        users_data.append(user_data)  # Add new player to users data
        
        # Sort the users alphabetically and by symbols, numbers, and characters
        users_data.sort(key=lambda user: (user["player_name"].strip().lower(), user["player_name"]))

        save_users(users_data)  # Save updated users data
        print(f"Created new account for {author}")

    return user_data

##### important variables #####
GACHA_PULL_PRICE = 1.99
MAX_PULLS = 5
GUARANTEE_AT = 25

##### Gacha Rates ######
gacha_rates = {
    "5-star": 0.02,
    "4-star": 0.05,
    "3-star": 0.15,
    "2-star": 0.33,
    "1-star": 0.50,
}

def pull(author, send_message, users_data):
    guarantee = False

    # Load or create the user's data
    user_data = get_user(author, users_data)

    # Check how many pulls the user has done today and the remaining pulls
    gacha_today = user_data.get("gacha", {}).get("today", 0)
    remaining_pulls = MAX_PULLS - gacha_today

    if remaining_pulls <= 0:
        send_message(f"{author}, you've already pulled {MAX_PULLS} times today. Please try again after midnight UTC.")
        #akailogger.log_to_file(f"{author}, you've already pulled {MAX_PULLS} times today. Please try again after midnight UTC.")
        return
    
    items = load_items()
    blades = load_blades()

    def roll_for_blade(chance):
        return random.random() < chance

    user_balance = check_balance(author)
    if user_balance is None:
        send_message(f"{author}, you don't have enough Akaiyen for a Gacha pull. You need {GACHA_PULL_PRICE} akaiyen for one pull. "
                     f"More info: https://akai.gikopoi.com/akai.py/akaiyen.html")
        #akailogger.log_to_file(f"{author}, you don't have enough Akaiyen for a Gacha pull. You need {GACHA_PULL_PRICE} akaiyen for one pull. "
        #             f"More info: https://akai.gikopoi.com/akai.py/akaiyen.html")
        return

    if user_balance < GACHA_PULL_PRICE:
        send_message(f"{author}, you don't have enough Akaiyen for a Gacha pull. You need {GACHA_PULL_PRICE} akaiyen for one pull. "
                     f"More info: https://akai.gikopoi.com/akai.py/akaiyen.html")
        #akailogger.log_to_file(f"{author}, you don't have enough Akaiyen for a Gacha pull. You need {GACHA_PULL_PRICE} akaiyen for one pull. "
        #             f"More info: https://akai.gikopoi.com/akai.py/akaiyen.html")
        return

    # charge user
    write_to_file(author, -GACHA_PULL_PRICE)  # Subtract GACHA_PULL_PRICE from balance
    lottery(GACHA_PULL_PRICE)

    pulled = None
    is_blade = False  # Track if a blade is pulled

    while pulled is None:  # Keep rolling until a valid item is obtained
        r_roll = random.random()

        if user_data["gacha"]["guarantee"] >= 24:
            print(f"{author}, you have a guaranteed 5-star item!")
            # Force a 5-star pull
            r_roll = 0.00
            guarantee = True

        # ROLLS
        if r_roll < gacha_rates["5-star"]:
            user_data["gacha"]["guarantee"] = 0
            if roll_for_blade(0.10) and any(blade["Rarity"] == "5-star" for blade in blades): 
                potential_blades = [blade for blade in blades if blade["Rarity"] == "5-star"]
                pulled = random.choice(potential_blades)
                is_blade = True
            else:
                pulled = random.choice([item for item in items if item["Rarity"] == "5-star"])

        elif r_roll < gacha_rates["5-star"] + gacha_rates["4-star"]:
            user_data["gacha"]["guarantee"] += 1
            if roll_for_blade(0.20) and any(blade["Rarity"] == "4-star" for blade in blades): 
                potential_blades = [blade for blade in blades if blade["Rarity"] == "4-star"]
                pulled = random.choice(potential_blades)
                is_blade = True
            else:
                pulled = random.choice([item for item in items if item["Rarity"] == "4-star"])

        elif r_roll < gacha_rates["5-star"] + gacha_rates["4-star"] + gacha_rates["3-star"]:
            user_data["gacha"]["guarantee"] += 1
            ### BIG BOY DECISION: 3-star blades do not exist, at least not from the gacha

            #if roll_for_blade(0.30) and any(blade["Rarity"] == "3-star" for blade in blades): 
            #    potential_blades = [blade for blade in blades if blade["Rarity"] == "3-star"]
            #    pulled = random.choice(potential_blades)
            #    is_blade = True
            #else:
            #    pulled = random.choice([item for item in items if item["Rarity"] == "3-star"])
            pulled = random.choice([item for item in items if item["Rarity"] == "3-star"])

        elif r_roll < gacha_rates["5-star"] + gacha_rates["4-star"] + gacha_rates["3-star"] + gacha_rates["2-star"]:
            user_data["gacha"]["guarantee"] += 1
            pulled = random.choice([item for item in items if item["Rarity"] == "2-star"])

        else:
            user_data["gacha"]["guarantee"] += 1
            pulled = random.choice([item for item in items if item["Rarity"] == "1-star"])

        # Check if the user already owns the blade (if a blade was rolled)
        if is_blade:
            # Ensure the blade has a 'blade_ID'
            if "blade_ID" not in pulled:
                send_message("Error: Pulled blade does not have a 'blade_ID'.")
                return

            # Check if the user already owns this blade by checking blade_ID under "blades" in user data
            user_blades = user_data.get("blades", {})
            # Reroll if the blade ID is already owned
            if str(pulled["blade_ID"]) in user_blades:  # Convert blade_ID to string for matching keys
                print(f"You already own the blade {pulled['blade_name']}. Rerolling...")
                pulled = None  # Reroll if blade already exists
                is_blade = False  # Reset flag to avoid infinite loop
                if guarantee == True:
                    user_data["gacha"]["guarantee"] = 24
                continue  # Skip to the next iteration of the loop

    # Debugging: Log the pulled item
    print(f"Item Pulled: {pulled}")

    if pulled is None:
        print(f"error with pulled.")
        return

    if is_blade:
        # Ensure the blade has an ID before adding it
        if "blade_ID" not in pulled:
            print(f"Error: Pulled blade does not have a 'blade_ID'.")
            return

        # Add the blade to the user's inventory
        add_to_blades(author, pulled, users_data)
        name = pulled["blade_name"]
    else:
        # Ensure the item has an ID before adding it
        if "item_ID" not in pulled:
            print(f"Error: Pulled item does not have an 'item_ID'.")
            return

        # Add the item to the user's inventory
        add_to_inventory(author, pulled, users_data)
        name = pulled["item_name"]

    # Increment the user's pull count for today
    user_data["gacha"]["today"] += 1
    user_data["gacha"]["total"] += 1

    # Save the updated Users data to users.json
    save_users(users_data)
    
    # output
    rarity = pulled.get("Rarity")

    url = f"https://akai.gikopoi.com/akai.py/items.html#{pulled.get('item_ID')}"

    if is_blade == True:
        url = f"https://akai.gikopoi.com/akai.py/blade.html#{pulled.get('blade_ID')}"

    pull_message = (f"[GACHAPON!] {author}, you pull: {name} ({rarity}) [ More details: {url} ] "
                   f"// [{remaining_pulls - 1} / {MAX_PULLS} pull(s) remaining for today] [you spent {GACHA_PULL_PRICE} akaiyen]")

    send_message(pull_message)
    #akailogger.log_to_file(pull_message)

def add_to_inventory(author, pulled, users_data):
    # find user
    user_index = next((index for index, user in enumerate(users_data) if user["player_name"].strip().lower() == author.strip().lower()), None)
    
    if user_index is None:
        # debug
        print(f"User {author} not found!")
        return

    user_data = users_data[user_index]
    
    # Get item_ID
    item_id = str(pulled["item_ID"])

    if "item_name" in pulled:
        # add to items
        if "items" not in user_data:
            user_data["items"] = {}

        if item_id in user_data["items"]:
            # increase quantity of existing item
            user_data["items"][item_id] += 1
        else:
            # add new item with qty 1
            user_data["items"][item_id] = 1

        # dictionary sort
        user_data["items"] = dict(sorted(user_data["items"].items(), key=lambda x: float(x[0]))) 

    else:
        # add to blades
        blade_id = len(user_data.get("blades", {})) + 1  # Generate a new blade ID (optional depending on your needs)
        if "blades" not in user_data:
            user_data["blades"] = {}
        user_data["blades"][str(blade_id)] = pulled

    save_users(users_data)

def add_to_blades(author, blade_pulled, users_data):
    """
    Add the pulled blade to the user's inventory.
    Ensures blades are stored using blade_ID and given default core_slots.
    Blades are stored in numerical order.
    """
    # find user
    user_index = next((index for index, user in enumerate(users_data) if user["player_name"].strip().lower() == author.strip().lower()), None)

    if user_index is None:
        print(f"User {author} not found!")
        return

    user_data = users_data[user_index]

    # Get the blade_ID
    blade_id = str(blade_pulled["blade_ID"])

    if "blades" not in user_data:
        user_data["blades"] = {}

    if blade_id not in user_data["blades"]:
        # Assign the blade with default core_slots
        user_data["blades"][blade_id] = {
            "core_slots": {
                "available": 7,
                "used": 0,
                "broken": 0
            }
        }

    # blade dictionary sort
    user_data["blades"] = dict(sorted(user_data["blades"].items(), key=lambda x: float(x[0])))

    save_users(users_data)

def get_guarantee(author, users_data):
    user_data = get_user(author, users_data)
    return user_data["gacha"].get("guarantee")

def cmd(author, namespace, send_message):

    message = namespace.strip()
    users_data = load_users()

    if message == ".gacha":
        pull(author, send_message, users_data)

    if message == ".gacha_rate":
        send_message(f"1 pull from Gachapon = {GACHA_PULL_PRICE} akaiyen // {MAX_PULLS} pulls per day")
        #akailogger.log_to_file(f"1 pull from Gachapon = {GACHA_PULL_PRICE} akaiyen // {MAX_PULLS} pulls per day")

    if message == ".guarantee":
        guarantee_count = get_guarantee(author, users_data)
        guarantee_output = GUARANTEE_AT - guarantee_count 
        send_message(f"{author}, if you don't get a 5-star in {guarantee_output} pulls, you will have a guaranteed 5-star pull!")
        #akailogger.log_to_file(f"{author}, if you don't get a 5-star in {guarantee_output} pulls, you will have a guaranteed 5-star pull!")

    if message == ".bag":
        # Manually replace spaces with '%20'
        encoded_author = author.replace(" ", "%20")
        send_message(f"{author}, you can access your inventory here: https://akai.gikopoi.com/akai.py/users.html#{encoded_author}")
        #akailogger.log_to_file(f"{author}, you can access your inventory here: https://akai.gikopoi.com/akai.py/users.html#{encoded_author}")