import json
import os
import time
from datetime import datetime, timedelta
import threading

directory = open(os.path.expanduser("~/akaipy-data/gacha_dir.txt"), "r")
directory = directory.read().splitlines()[0].strip()

logfn = os.path.expanduser('~/akaipy-data/reset.txt')

def log_resets(message):
    try:
        with open(logfn, 'a', encoding='utf-8') as log_file:
            log_file.write(f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    except Exception as e:
        print(f"Error writing to log file: {e}")

def reset_today_pull():
    users_file = os.path.expanduser(f"{directory}/users.json")

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

        # Log successful reset
        print(f"[*] [UTC MIDNIGHT TODAY'S GACHA PULL RESET]")
        log_resets("[*] [UTC MIDNIGHT TODAY'S GACHA PULL RESET]")

    except Exception as e:
        print(f"Error: {e}")
        log_resets(f"Error: {e}")

def sleep():
    now = datetime.utcnow()
    
    target_time = datetime(now.year, now.month, now.day) + timedelta(days=1)

    sleep_duration = (target_time - now).total_seconds()

    hours = int(sleep_duration // 3600)
    minutes = int((sleep_duration % 3600) // 60)
    seconds = int(sleep_duration % 60)

    print(f"[*] Timer sleeping for {hours} hrs, {minutes} min, {seconds} sec until {target_time} UTC.")
    log_resets(f"[*] Timer sleeping for {hours} hrs, {minutes} min, {seconds} sec until {target_time} UTC.")

    time.sleep(sleep_duration)

    reset_today_pull()

    print("[*] END RESET")
    log_resets("[*] END RESET")

    # Start the timer again for the next day
    sleep()

def start():
    if not os.path.exists(logfn):
        open(logfn, 'w').close()

    reset_thread = threading.Thread(target=sleep, daemon=True)
    reset_thread.start()

    log_resets("[*] Timer started successfully.")