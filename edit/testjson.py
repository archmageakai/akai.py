import json
import os

# Define the paths
users_file_path = os.path.expanduser('~/akaipy/data/users.json')
blade_file_path = os.path.expanduser('~/akaipy/data/blade.json')

# Load blade data from the file
with open(blade_file_path, 'r') as blade_file:
    blade_data = json.load(blade_file)

# Create a dictionary to map blade_ID to blade_name for quick lookup
blade_id_to_name = {str(blade["blade_ID"]): blade["blade_name"] for blade in blade_data["blades"]}

# Load user data from the file
with open(users_file_path, 'r') as users_file:
    users_data = json.load(users_file)

# For each blade in Akai's inventory, print the blade name corresponding to the blade_ID
akai_blades = users_data["users"][0]["blades"]
for blade_id in akai_blades.keys():
    blade_id_str = str(blade_id)
    if blade_id_str in blade_id_to_name:
        print(f"Blade ID {blade_id_str}: {blade_id_to_name[blade_id_str]}")

# Add blades to Akai's inventory if the blade_ID is not already in the inventory
akai_blade_ids = akai_blades.keys()
for blade in blade_data["blades"]:
    blade_id = str(blade["blade_ID"])  # Convert blade_ID to string to match the keys in Akai's inventory
    if blade_id not in akai_blade_ids:
        users_data["users"][0]["blades"][blade_id] = {
            "core_slots": {"available": 7, "used": 0, "broken": 0}  # Default core slots for new blades
        }

# Sort the blades by blade_ID numerically
users_data["users"][0]["blades"] = dict(sorted(users_data["users"][0]["blades"].items(), key=lambda item: int(item[0])))

# Write the sorted user data back to the file
with open(users_file_path, 'w') as users_file:
    json.dump(users_data, users_file, indent=4)

# Debug
print(json.dumps(users_data, indent=4))