import json
import os
import time
from datetime import datetime, timedelta
import threading

def reset_today_pull():
    users_file = os.path.expanduser("./data/users.json")

    try:
        if not os.path.exists(users_file):
            print(f"Error: {users_file} does not exist.")
            return
        
        with open(users_file, 'r', encoding="utf-8") as file:
            data = json.load(file)

        if "users" in data and isinstance(data["users"], list):
            for user in data["users"]:
                if "gacha" in user and "today" in user["gacha"]:
                    user["gacha"]["today"] = 0

        with open(users_file, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    except Exception as e:
        print(f"Error: {e}")

def sleep():

    now = datetime.utcnow()
    
    # Set target time to midnight UTC of the next day
    target_time = datetime(now.year, now.month, now.day) + timedelta(days=1)

    # Calculate sleep duration in seconds
    sleep_duration = (target_time - now).total_seconds()

    # Convert sleep duration to hours, minutes, and seconds
    hours = int(sleep_duration // 3600)
    minutes = int((sleep_duration % 3600) // 60)
    seconds = int(sleep_duration % 60)

    print(f"[*] Timer sleeping for {hours} hrs, {minutes} min, {seconds} sec until {target_time} UTC.")

    # Sleep until the target time
    time.sleep(sleep_duration)

    # Reset "today" values after waking up
    reset_today_pull()
    print(f"[*] [UTC MIDNIGHT TODAY'S GACHA PULL RESET]")

def start():

    reset_thread = threading.Thread(target=sleep, daemon=True)
    reset_thread.start()