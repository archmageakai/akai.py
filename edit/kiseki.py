#!/usr/bin/env python3

import os
import random

class Quartz:
    def __init__(self, name, element, value):
        self.name = name
        self.element = element
        self.value = value

class OrbmentSlot:
    def __init__(self, element):
        self.element = element
        self.quartz = None

    def install_quartz(self, quartz):
        if self.element == "Neutral" or self.element == quartz.element:
            self.quartz = quartz
        else:
            print("Quartz does not match the elemental slot")

class Orbment:
    def __init__(self, slots):
        self.slots = slots
        self.lines = []

    def add_line(self, line):
        self.lines.append(line)

class Line:
    def __init__(self, color):
        self.color = color
        self.slots = []

    def add_slot(self, slot):
        self.slots.append(slot)

    def get_total_elemental_value(self, element):
        total_value = 0
        for slot in self.slots:
            if slot.quartz and slot.quartz.element == element:
                total_value += slot.quartz.value
        return total_value

class Character:
    def __init__(self, name, hp, ep, cp, orbment):
        self.name = name
        self.hp = hp
        self.ep = ep
        self.cp = cp
        self.orbment = orbment

    def display_stats(self):
        print(f"{self.name}'s stats:")
        print(f"HP: {self.hp}")
        print(f"EP: {self.ep}")
        print(f"CP: {self.cp}")
        print(f"Orbment:")
        for i, slot in enumerate(self.orbment.slots):
            if slot.quartz:
                print(f"Slot {i+1}: {slot.element} - {slot.quartz.name} ({slot.quartz.element})")
            else:
                print(f"Slot {i+1}: {slot.element} - Empty")
        if self.orbment.lines:
            print(f"Lines:")
            for i, line in enumerate(self.orbment.lines):
                print(f"Line {i+1}: {line.color}")
                for slot in line.slots:
                    if slot.quartz:
                        print(f"  - {slot.quartz.name} ({slot.quartz.element})")
                    else:
                        print(f"  - Empty")

class Enemy:
    def __init__(self, name, hp):
        self.name = name
        self.hp = hp

    def display_stats(self):
        print(f"{self.name}'s stats:")
        print(f"HP: {self.hp}")

    def attack(self, party):
        target = random.choice(party.members)
        damage = random.randint(1, 8)
        target.hp -= damage
        print(f"{self.name} attacks {target.name} for {damage} damage!")

class Magic:
    def __init__(self, name, element, ep_cost, damage, required_quartz):
        self.name = name
        self.element = element
        self.ep_cost = ep_cost
        self.damage = damage
        self.required_quartz = required_quartz

    def can_cast(self, character):
        for quartz in self.required_quartz:
            total_value = 0
            if character.orbment.lines:
                for line in character.orbment.lines:
                    total_value += line.get_total_elemental_value(quartz.element)
            if total_value < quartz.value:
                return False
        return True

    def cast(self, character, enemy):
        if character.ep >= self.ep_cost:
            ep_sufficient = True
        else:
            ep_sufficient = False
        if self.can_cast(character):
            quartz_sufficient = True
        else:
            quartz_sufficient = False
        if ep_sufficient and quartz_sufficient:
            character.ep -= self.ep_cost
            enemy.hp -= self.damage
            print(f"{character.name} casts {self.name}!")
            return True
        else:
            if not ep_sufficient:
                print(f"{character.name} doesn't have enough EP to cast {self.name}!")
            if not quartz_sufficient:
                print(f"{character.name} doesn't have the required quartz to cast {self.name}!")
            return False

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_selection():
    print("\nSelect an action:")
    print("[A] Attack")
    print("[C] Cast Spell")
    print("[M] Move")
    print("[I] Use Item")
    print("[R] Run")

def display_spells(spells):
    print("\nAvailable spells:")
    for i, spell in enumerate(spells):
        print(f"{i+1}. {spell.name} (EP: {spell.ep_cost}, Damage: {spell.damage})")

def redraw_stats(party, enemy):
    clear_screen()
    print("\n" * 5)
    for member in party.members:
        member.display_stats()
        print("\n" * 5)
    enemy.display_stats()

class Party:
    def __init__(self):
        self.members = []

    def add_member(self, member):
        self.members.append(member)

    def remove_member(self, member):
        self.members.remove(member)

def main():
    estelle_slot1 = OrbmentSlot("Neutral")
    estelle_slot2 = OrbmentSlot("Neutral")
    estelle_slot3 = OrbmentSlot("Neutral")
    estelle_slot4 = OrbmentSlot("Neutral")
    estelle_slot5 = OrbmentSlot("Neutral")
    estelle_slot6 = OrbmentSlot("Neutral")

    estelle_orbment = Orbment([estelle_slot1, estelle_slot2, estelle_slot3, estelle_slot4, estelle_slot5, estelle_slot6])

    yellow_line = Line("Yellow")
    blue_line = Line("Blue")

    yellow_line.add_slot(estelle_slot1)
    yellow_line.add_slot(estelle_slot2)
    blue_line.add_slot(estelle_slot3)
    blue_line.add_slot(estelle_slot4)

    estelle_orbment.add_line(yellow_line)
    estelle_orbment.add_line(blue_line)

    stone_quartz = Quartz("Stone Quartz", "Earth", 1)
    water_quartz = Quartz("Water Quartz", "Water", 1)
    fire_quartz = Quartz("Fire Quartz", "Fire", 1)

    estelle_slot1.install_quartz(stone_quartz)
    estelle_slot3.install_quartz(water_quartz)

    estelle = Character("Estelle Bright", 100, 100, 100, estelle_orbment)
    joshua_orbment = Orbment([])
    joshua_orbment_slot = OrbmentSlot("Neutral")
    joshua_orbment_slot.install_quartz(fire_quartz)
    joshua_orbment.slots.append(joshua_orbment_slot)
    joshua = Character("Joshua Bright", 100, 100, 100, joshua_orbment)
    enemy = Enemy("Goblin", 50)

    stone_hammer = Magic("Stone Hammer", "Earth", 10, 20, [Quartz("Stone Quartz", "Earth", 1)])
    fire_bolt = Magic("Fire Bolt", "Fire", 15, 30, [Quartz("Fire Quartz", "Fire", 1)])
    aqua_bleed = Magic("Aqua Bleed", "Water", 12, 25, [Quartz("Water Quartz", "Water", 1)])

    spells = [stone_hammer, fire_bolt, aqua_bleed]

    party = Party()
    party.add_member(estelle)
    party.add_member(joshua)

    while True:
        redraw_stats(party, enemy)
        for member in party.members:
            display_selection()
            action = input(f"{member.name}, enter your choice: ")
            if action.upper() == "C":
                display_spells(spells)
                spell_choice = int(input("Enter the number of the spell: ")) - 1
                if spell_choice >= 0 and spell_choice < len(spells):
                    if spells[spell_choice].cast(member, enemy):
                        redraw_stats(party, enemy)
                else:
                    print("Invalid spell choice!")
            elif action.upper() == "A":
                print("Attack stubbed for now")
            elif action.upper() == "M":
                print("Move stubbed for now")
            elif action.upper() == "I":
                print("Use Item stubbed for now")
            elif action.upper() == "R":
                print("Run stubbed for now")
        enemy.attack(party)
        redraw_stats(party, enemy)

if __name__ == "__main__":
    main()