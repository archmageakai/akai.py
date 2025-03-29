import json
import os
import time
from datetime import datetime, timedelta
import threading

bot_no = None

def set_bot_no(no):
    """Set bot_no from main script."""
    global bot_no
    bot_no = no
    print(f"[reset] sees bot as BOT NO: {bot_no}")

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
    # no smegaphone
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

        # revert back, must pass smegaphone in param
        #smegaphone("ANNOUNCEMENT! The gacha game daily pulls has reset. Have fun with Gachapon! ^o^")

    except Exception as e:
        print(f"Error: {e}")
        log_resets(f"Error: {e}")

def sleep(smegaphone):
    while True:
        log_resets("CHECK LOOP")
        now = datetime.utcnow()

        # 24 hr timer
        #target_time = datetime(now.year, now.month, now.day) + timedelta(days=1)

        #test timer
        target_time = now + timedelta(seconds=30)

        sleep_duration = (target_time - now).total_seconds()

        hours = int(sleep_duration // 3600)
        minutes = int((sleep_duration % 3600) // 60)
        seconds = int(sleep_duration % 60)

        print(f"[*] Timer sleeping for {hours} hrs, {minutes} min, {seconds} sec until {target_time} UTC.")
        log_resets(f"[*] Timer sleeping for {hours} hrs, {minutes} min, {seconds} sec until {target_time} UTC.")

        time.sleep(sleep_duration)

        #reset_today_pull(smegaphone)
        if bot_no == 1:
            print("[*] Resetting today's pull because bot_no is 1")
            log_resets("[*] Resetting today's pull because bot_no is 1")
            reset_today_pull()

            print("[*] END RESET")
            log_resets("[*] END RESET")
    
        smegaphone("ANNOUNCEMENT! The gacha game daily pulls has reset. Have fun with Gachapon! ^o^")

        print("[*] timer restarted")
        log_resets("[*] timer restarted")

def start(smegaphone):
    if not os.path.exists(logfn):
        open(logfn, 'w').close()

    reset_thread = threading.Thread(target=sleep, args=(smegaphone,), daemon=True)
    reset_thread.start()

    log_resets("[*] Timer started successfully.")

def force_reset():
    reset_today_pull()



"""def checkBotNo(author, namespace, send_message):
    
    message = namespace.strip()

    if author == "Akai":
        if message == ".check":
            send_message(f"bot no is: {bot_no}")"""