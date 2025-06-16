#!/usr/bin/env python3

import os
import random

# =============================
# CORE DATA STRUCTURES
# =============================

class Quartz:
    def __init__(self, name, element, value=1):
        self.name = name
        self.element = element
        self.value = value

class OrbmentSlot:
    def __init__(self, element=None):
        self.element = element  # None = Neutral
        self.quartz = None
        self.connected_slots = []

    def install_quartz(self, quartz):
        if self.element is None or self.element == quartz.element:
            self.quartz = quartz
            return True
        return False

    def connect_to(self, other_slot):
        if other_slot not in self.connected_slots:
            self.connected_slots.append(other_slot)
            other_slot.connected_slots.append(self)

class OrbmentLine:
    def __init__(self, color):
        self.color = color
        self.slots = []

    def add_slot(self, slot):
        self.slots.append(slot)

    def get_total_element_value(self, element):
        total = 0
        for slot in self.slots:
            if slot.quartz and slot.quartz.element == element:
                total += slot.quartz.value
        return total

class Orbment:
    def __init__(self, slots, lines):
        self.slots = slots
        self.lines = lines

    def can_cast(self, spell):
        for line in self.lines:
            quartz_count = {}
            for slot in line.slots:
                if slot.quartz:
                    q = slot.quartz
                    if q.element in quartz_count:
                        quartz_count[q.element] += q.value
                    else:
                        quartz_count[q.element] = q.value
            meets_requirement = True
            for req in spell.required_quartz:
                if req.element not in quartz_count or quartz_count[req.element] < req.value:
                    meets_requirement = False
                    break
            if meets_requirement:
                return True
        return False

# =============================
# SPELL SYSTEM
# =============================

class Spell:
    def __init__(self, name, element, ep_cost, power=0, effect=None, target_type="single", required_quartz=None):
        self.name = name
        self.element = element
        self.ep_cost = ep_cost
        self.power = power
        self.effect = effect
        self.target_type = target_type
        self.required_quartz = required_quartz or []

    def can_cast(self, caster):
        if caster.ep < self.ep_cost:
            return False
        if not caster.orbment.can_cast(self):
            return False
        return True

    def cast(self, caster, target):
        if not self.can_cast(caster):
            print(f"{caster.name} cannot cast {self.name}!")
            return False
        caster.ep -= self.ep_cost
        damage = int(caster.atk * self.power)
        if damage:
            print(f"{caster.name} casts {self.name} on {target.name} for {damage} damage!")
            target.take_damage(damage)
        if self.effect:
            target.apply_status(self.effect)
        return damage

# =============================
# STATUS EFFECTS
# =============================

class StatusEffect:
    def __init__(self, name, duration, on_apply, on_tick, on_expire=None):
        self.name = name
        self.duration = duration  # duration in seconds.  0 is indeterminate / infinite
        self.on_apply = on_apply
        self.on_tick = on_tick
        self.on_expire = on_expire

    def apply(self, target):
        self.on_apply(target)

    def tick(self, target):
        self.on_tick(target)
        self.duration -= 1
        if self.duration <= 0 and self.on_expire:
            self.on_expire(target)

# Hold/Freeze effect
def hold_apply(target):
    print(f"{target.name} is held! (Turn delayed by 50 units)")
    target.next_action_time += 50

def hold_tick(target):
    pass

def hold_expire(target):
    print(f"{target.name} is free from hold!")

hold_effect = StatusEffect("Hold", 1, hold_apply, hold_tick, hold_expire)

# Haste effect
def haste_apply(target):
    print(f"{target.name} is HASTED! Speed increased to 1.2")
    target.speed = 1.2

def haste_tick(target):
    pass

def haste_expire(target):
    print(f"{target.name}'s Haste wears off. Speed returns to normal.")
    target.speed = 1.0

haste_effect = StatusEffect("Haste", 3, haste_apply, haste_tick, haste_expire)

# Slow effect
def slow_apply(target):
    print(f"{target.name} is SLOWED! Speed reduced to 0.8")
    target.speed = 0.8

def slow_tick(target):
    pass

def slow_expire(target):
    print(f"{target.name}'s Slow wears off. Speed returns to normal.")
    target.speed = 1.0

slow_effect = StatusEffect("Slow", 3, slow_apply, slow_tick, slow_expire)


# Dead effect
def dead_apply(target):
    print(f"{target.name} is KO'd!")
    target.speed = 0.8

def dead_tick(target):
    pass

def dead_undo(target):
    print(f"{target.name} is revived!")
    target.speed = 1.0

dead_effect = StatusEffect("Dead", 0, hold_apply, hold_tick, hold_expire)

# =============================
# CHARACTER CLASS
# =============================

class Character:
    def __init__(self, name, hp, ep, cp, atk, defense, agility, initiative, 
                 speed=1.0, orbment=None, status_effects=None):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.ep = ep
        self.max_ep = ep
        self.cp = cp
        self.max_cp = cp
        self.atk = atk
        self.defense = defense
        self.base_agility = agility
        self.initiative = initiative
        self.speed = speed
        self.time = 0
        self.next_action_time = self.initiative / self.speed
        self.orbment = orbment or Orbment([], [])
        self.status_effects = status_effects if status_effects else []

    def apply_status(self, effect):
        for se in self.status_effects:
            if se.name == effect.name:
                se.duration = max(se.duration, effect.duration)
                return
        self.status_effects.append(effect)
        effect.apply(self)

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.apply_status(dead_effect)

    def display_stats(self):
        statuses = ", ".join([se.name for se in self.status_effects]) if self.status_effects else "None"
        stats_line = f"{self.name}: HP={self.hp}/{self.max_hp} | EP={self.ep}/{self.max_ep} | Status: {statuses}"

        orbment_lines = []
        for line in self.orbment.lines:
            orbment_str = " - ".join(f"[{slot.quartz.name}]" if slot.quartz else "[Empty]" for slot in line.slots)
            orbment_lines.append(f"  {line.color}: {orbment_str}")
        return [stats_line] + orbment_lines

    def get_available_actions(self):
        actions = {
            "A": ("Attack", self.can_attack),
            "C": ("Cast", self.can_cast),
            "D": ("Defend", self.can_defend),
            "I": ("Item", self.can_use_item),
            "R": ("Run", self.can_run),
        }
        return {k: (v[0], v[1]()) for k, v in actions.items()}

    def can_attack(self):
        return True

    def can_cast(self):
        return any(spell.can_cast(self) for spell in [fire_bolt, stasis, haste_spell, slow_spell])

    def can_defend(self):
        return True

    def can_use_item(self):
        return False  # Stub

    def can_run(self):
        return False  # Stub

# =============================
# COMBAT LOOP
# =============================

def clear_screen():
    os.system('clear')

def display_battle(party, enemies, participants, global_time):
    clear_screen()
    print("=== CURRENT STATS ===\n")
    for member in party:
        print(member.display_stats())
    print(f"\n")
    for enemy in enemies:
        print(enemy.display_stats())
    print("\n=== TURN ORDER ===")
    for p in sorted(participants, key=lambda p: p.next_action_time if p.hp > 0 else float('inf')):
        #if p.hp <= 0:
        #    print(f"{p.name} (KO)")
        #else:
        if p.hp > 0:
            remaining_time = p.next_action_time - global_time
            print(f"{p.name} (Time: {remaining_time:.0f}s)")

def select_target(attacker, enemies):
    alive_enemies = [e for e in enemies if e.hp > 0]
    if not alive_enemies:
        return None
    print("\nSelect a target:")
    for i, enemy in enumerate(alive_enemies):
        print(f"{i+1}. {enemy.name} (HP: {enemy.hp})")
    choice = input("Enter number: ")
    if choice.isdigit() and 0 < int(choice) <= len(alive_enemies):
        return alive_enemies[int(choice) - 1]
    return alive_enemies[0]

def select_spell(caster, available_spells):
    print("\nAvailable Spells:")
    valid_spells = []
    for i, spell in enumerate(available_spells):
        if spell.can_cast(caster):
            valid_spells.append((i, spell))
            print(f"{i+1}. {spell.name} (EP: {spell.ep_cost}, Power: {spell.power})")
        else:
            print(f"{i+1}. {spell.name} - [LOCKED - Missing Quartz or EP]")
    if not valid_spells:
        print("No spells available to cast.")
        return None
    choice = input("Select spell: ")
    if choice.isdigit():
        idx = int(choice) - 1
        for i, spell in valid_spells:
            if i == idx:
                return spell
    return None

def combat_loop(party, enemies):
    participants = party + enemies
    global_time = 0

    # Initialize next action time
    for p in participants:
        p.next_action_time = p.initiative / p.speed

    while True:
        display_battle(party, enemies, participants, global_time)

        # Check win/lose conditions
        if all(e.hp <= 0 for e in enemies):
            print("\nCongratulations, heroes!")
            print("You have won 500 gikocoins!")
            input("\nPress Enter to return to main menu...")
            return True
        if all(p.hp <= 0 for p in party):
            print("\nYou have DIEDED! Play again? y/N")
            choice = input(">> ").strip().lower()
            if choice == 'y':
                return False
            else:
                print("Thanks for playing!")
                exit(0)

        # Process next available participant (Should we check for dead status or hp?)
        for p in sorted(participants, key=lambda p: p.next_action_time if p.hp > 0 else float('inf')):
            if p.hp <= 0:
                continue

            # Advance global time
            if global_time < p.next_action_time:
                global_time = p.next_action_time

            # Apply status effects
            for effect in list(p.status_effects):
                effect.tick(p)
                if effect.duration <= 0:
                    p.status_effects.remove(effect)

            if p.hp <= 0:
                continue

            # Perform action
            if p in party:
                print(f"\n{p.name}'s Turn:")
                actions = p.get_available_actions()
                for key, (name, available) in actions.items():
                    if available:
                        print(f"{name[0]}: {name}")
                    else:
                        print(f"{name[0]}: {name.lower()}")
                action = input("Choose action: ").lower()
                if action == 'c':
                    spell = select_spell(p, [fire_bolt, stasis, haste_spell, slow_spell])
                    if spell:
                        target = select_target(p, enemies)
                        if target:
                            spell.cast(p, target)
                elif action == 'a':
                    target = select_target(p, enemies)
                    if target:
                        print(f"{p.name} attacks {target.name} for {p.atk} damage!")
                        target.take_damage(p.atk)
                else:
                    print(f"{p.name} did nothing this turn.")
            else:
                target = random.choice([p for p in party if p.hp > 0])
                damage = p.atk
                print(f"{p.name} attacks {target.name} for {damage} damage!")
                target.take_damage(damage)
                if target.hp <= 0:
                    print(f"{target.name} collapses!")

            # Recalculate next action time
            p.next_action_time = global_time + (p.initiative / p.speed)
            break

# =============================
# CHARACTER ORBMENT SETUP
# =============================

def setup_estelle():
    slots = [OrbmentSlot(None) for _ in range(6)]
    yellow_line = OrbmentLine("Yellow")
    blue_line = OrbmentLine("Blue")

    yellow_line.add_slot(slots[0])
    yellow_line.add_slot(slots[1])
    blue_line.add_slot(slots[2])
    blue_line.add_slot(slots[3])

    fire_q = Quartz("Fire Quartz", "Fire", 2)
    slots[0].install_quartz(fire_q)

    return Orbment(slots, [yellow_line, blue_line])

def setup_joshua():
    slots = [OrbmentSlot("Time"), OrbmentSlot("Time"), OrbmentSlot(None), OrbmentSlot(None), OrbmentSlot(None), OrbmentSlot(None)]
    time_line = OrbmentLine("Time")
    neutral_line = OrbmentLine("Neutral")

    time_line.add_slot(slots[0])
    time_line.add_slot(slots[1])
    neutral_line.add_slot(slots[2])
    neutral_line.add_slot(slots[3])

    time_q = Quartz("Time Crystal", "Time", 3)
    slots[0].install_quartz(time_q)

    return Orbment(slots, [time_line, neutral_line])

# =============================
# SAMPLE SPELLS
# =============================

fire_bolt = Spell("Fire Bolt", "Fire", 10, power=1.5, target_type="single", required_quartz=[Quartz("Fire Quartz", "Fire", 2)])
stasis = Spell("Stasis", "Time", 20, effect=hold_effect, target_type="single", required_quartz=[Quartz("Time Crystal", "Time", 3)])
haste_spell = Spell("Haste", "Time", 25, effect=haste_effect, target_type="single", required_quartz=[Quartz("Time Crystal", "Time", 2)])
slow_spell = Spell("Slow", "Time", 20, effect=slow_effect, target_type="single", required_quartz=[Quartz("Time Crystal", "Time", 2)])

# =============================
# MAIN FUNCTION
# =============================

def main():
    while True:
        estelle_orbment = setup_estelle()
        joshua_orbment = setup_joshua()

        estelle = Character("Estelle Bright", 200, 100, 50, 15, 10, 29, 20, orbment=estelle_orbment)
        joshua = Character("Joshua Bright", 180, 100, 50, 18, 12, 23, 25, orbment=joshua_orbment)

        party = [estelle, joshua]

        goblin_count = random.randint(1, 4)
        enemies = [Character(f"Goblin {i+1}", 50, 0, 0, 10, 5, random.randint(20, 40),23) for i in range(goblin_count)]

        result = combat_loop(party, enemies)
        if result:
            break

if __name__ == "__main__":
    main()