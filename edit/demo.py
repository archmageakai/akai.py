import random
import json

# Define generic blades
blades = [
    {"name": "Pyra", "role": "Attacker", "element": "Fire", "HP": 100, "EP": 30, "ATK": 40, "DEF": 10},
    {"name": "Dromarch", "role": "Healer", "element": "Water", "HP": 120, "EP": 50, "ATK": 20, "DEF": 15},
    {"name": "Brighid", "role": "Defender", "element": "Ice", "HP": 150, "EP": 20, "ATK": 25, "DEF": 30},
]

items = [
    {"id": 1, "name": "HP Potion", "effect": "restore_hp", "amount": 30},
    {"id": 2, "name": "EP Potion", "effect": "restore_ep", "amount": 10},
]

# Combine stats
def combined_stats(blades):
    stats = {"HP": 0, "EP": 0, "ATK": 0, "DEF": 0}
    for b in blades:
        for key in stats:
            stats[key] += b[key]
    return stats

# Simple monster
monster = {"name": "Demon Lord", "HP": 1000, "ATK": 50, "DEF": 25}

# Element combos dictionary (order matters)
combos = {
    ("Fire", "Fire", "Water"): {"name": "Steam Burst", "damage": 170},
    ("Ice", "Ice", "Fire"): {"name": "Frost Flame", "damage": 150},
    ("Water", "Electric", "Fire"): {"name": "Thunder Steam", "damage": 180},
}

element_stack = []

player_stats = combined_stats(blades)
player_current_hp = player_stats["HP"]
player_current_ep = player_stats["EP"]

partial_guard_reduction = 0
guard_active = False

def calculate_damage(atk, def_):
    dmg = atk - def_ // 2
    return max(1, dmg)

def show_status():
    print(f"\nPlayer HP: {player_current_hp}/{player_stats['HP']} | EP: {player_current_ep}/{player_stats['EP']}")
    print(f"Monster HP: {monster['HP']}/{1000}")
    print(f"Element Stack: {' '.join(f'[{e}]' for e in element_stack) if element_stack else '(empty)'}\n")

def get_blade_by_role(role):
    for b in blades:
        if b["role"].lower() == role.lower():
            return b
    return None

def perform_attack():
    attackers = [b for b in blades if b["role"].lower() == "attacker"]
    if not attackers:
        #print("> No attacker blades found!")
        return

    for attacker in attackers:
        dmg = calculate_damage(attacker["ATK"], monster["DEF"])
        monster["HP"] -= dmg
        print(f"> {attacker['name']} attacks Demon Lord for {dmg} damage!")

def perform_guard():
    global partial_guard_reduction

    defenders = [b for b in blades if b["role"].lower() == "defender"]
    if not defenders:
        #print("> No defender blades found!")
        return

    # Sum individual DEF contributions (capped after total)
    total_def = sum(d["DEF"] for d in defenders)
    partial_guard_reduction = min(total_def * 0.5, 35)  # Cap max reduction to 35

    names = ", ".join(d["name"] for d in defenders)
    print(f"> {names} brace to reduce incoming damage by {int(partial_guard_reduction)}!")

def perform_heal():
    global player_current_hp
    heal_amount = 20  # simple flat heal
    total_heal = 0

    healers = [b for b in blades if b["role"].lower() == "healer"]
    if not healers:
        #print("> No healer blades available!")
        return

    for healer in healers:
        if player_current_hp >= player_stats["HP"]:
            break  # Stop if already at full HP
        before = player_current_hp
        player_current_hp = min(player_stats["HP"], player_current_hp + heal_amount)
        healed = player_current_hp - before
        total_heal += healed
        print(f"> {healer['name']} heals for {healed} HP!")

    if total_heal == 0:
        print("> Healing had no effect — HP is already full.")


def all_guard():
    global guard_active
    guard_active = True
    print("> All blades brace for impact! Incoming damage will be reduced this turn.")

def perform_skill():
    global player_current_ep, element_stack
    if player_current_ep < 3:
        print("> Not enough EP to use skill!")
        return
    player_current_ep -= 3
    chosen_blade = random.choice(blades)
    element_stack.append(chosen_blade["element"])
    if len(element_stack) > 3:
        element_stack.pop(0)
    print(f"> Skill used! Element '{chosen_blade['element']}' added to stack.")

def use_item(item_id):
    global player_current_hp, player_current_ep

    # Find the item with the given ID
    item = next((i for i in items if i["id"] == item_id), None)
    if not item:
        print("> Invalid item ID!")
        return False  # tell the turn() function not to advance

    if item["effect"] == "restore_hp":
        old_hp = player_current_hp
        player_current_hp = min(player_stats["HP"], player_current_hp + item["amount"])
        healed = player_current_hp - old_hp
        print(f"> Used {item['name']}! Restored {healed} HP.")
    elif item["effect"] == "restore_ep":
        old_ep = player_current_ep
        player_current_ep = min(player_stats["EP"], player_current_ep + item["amount"])
        restored = player_current_ep - old_ep
        print(f"> Used {item['name']}! Restored {restored} EP.")
    else:
        print(f"> {item['name']} used, but nothing happened.")
    
    return True  # successful item use

# Load combos from combo.json
with open("combo.json", "r") as f:
    combos = json.load(f)

def perform_combo():
    global element_stack, monster
    if len(element_stack) != 3:
        print("> Combo not ready! Need 3 elements.")
        return
    sorted_elements = sorted(element_stack)
    combo_key = str(sorted_elements)  # Convert sorted list to string as in JSON keys

    if combo_key in combos:
        combo = combos[combo_key]
        monster["HP"] -= combo["damage"]
        print(f"> Combo '{combo['name']}' triggered! Demon Lord takes {combo['damage']} damage!")
    else:
        print("> No combo matched. The elements fizzled out...")
    element_stack = []

def monster_attack():
    global player_current_hp, guard_active, partial_guard_reduction
    dmg = calculate_damage(monster["ATK"], player_stats["DEF"])
    
    if guard_active:
        dmg = dmg // 2
        print(f"> Guard reduced the damage by half!")
    elif partial_guard_reduction > 0:
        dmg = max(1, int(dmg - partial_guard_reduction))

    player_current_hp -= dmg
    print(f"> Demon Lord attacks you for {dmg} damage!")

    # Reset guards
    guard_active = False
    partial_guard_reduction = 0

def turn(command):
    print(f"\n-- Turn: {command} --")
    advance_turn = True

    if command.strip() == "1": # attack
        perform_attack()
        perform_heal()
        perform_guard()
    elif command.strip() == "2": #guard
        all_guard()
    elif command.strip() == "3": #skill
        perform_skill()
    elif command.strip() == "4" or (command.startswith("4 ") and command[2:].strip().isdigit()): #item
        parts = command.split()
        if len(parts) == 2 and parts[1].isdigit():
            success = use_item(int(parts[1]))
            if not success:
                advance_turn = False  # invalid item, don't advance
        else:
            print("> Usage: 4 <ID>")
            print("> Available items:")
            for item in items:
                print(f"  {item['id']}: {item['name']} - {item['effect']} +{item['amount']}")
            advance_turn = False  # Don't trigger monster attack
    elif command.strip() == "5".strip(): #combo
        perform_combo()
    else:
        print("> Unknown command!")
        advance_turn = False
    
    if advance_turn:
        monster_attack()

    if player_current_hp <= 0:
        print("\nYou have been defeated!")
        return False
    if monster["HP"] <= 0:
        print("\nYou defeated the Demon Lord!")
        return False
    
    show_status()
    return True

def main():
    print("Welcome")
    show_status()
    while True:
        cmd = input("Enter command (1. attack, 2. guard, 3. skill, 4. item, 5. combo): ").strip()
        if not turn(cmd):
            break

if __name__ == "__main__":
    main()