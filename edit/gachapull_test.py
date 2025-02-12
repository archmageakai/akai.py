import json
import os

users_file_path = os.path.expanduser('~/akaipy/data/users.json')

with open(users_file_path, 'r') as users_file:
    users_data = json.load(users_file)

pull = input("Do you want to do a pull? (y/n): ").strip().lower()

if pull == 'y':

    gacha_data = users_data["users"][1]["gacha"]
    
    gacha_data["today"] += 1
    print(f"TODAY: {gacha_data['today']}")

    gacha_data["guarantee"] += 1
    print(f"How many pulls without 5 star: {gacha_data['guarantee']}")

    gacha_data["total"] += 1
    print(f"Total: {gacha_data['total']}")
    
    if gacha_data["guarantee"] >= 25:
        gacha_data["guarantee"] = 0
        print("Guarantee reset to 0! Here is 5 star guarantee.")

with open(users_file_path, 'w') as users_file:
    json.dump(users_data, users_file, indent=4)

dump = input("Dump data? (y/n): ").strip().lower()

if dump == 'y':
        print("Updated data:")
        print(json.dumps(users_data, indent=4))