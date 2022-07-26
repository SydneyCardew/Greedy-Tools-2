from random import shuffle
from random import randint
import re


class Card:

    def __init__(self, index, card_line):
        self.number = index
        self.name = card_line[0]
        self.type = card_line[1]
        self.game_size = int(card_line[2][0])

        if re.search(r'(\d+)G/(\d+)G/(\d+)G', card_line[3]):
            self.rewards = [int(x) for x in card_line[3].replace('G', '').split("/")]
        else:
            self.rewards = None

        if card_line[3] == 'Worth 100G ':
            self.rewards = [100, 100, 100]

        if re.search(r'(\d/\d/\d\s[M|E|S][A|Y|N|T])', card_line[3]):
            hazard_strings = re.findall(r'(\d/\d/\d\s..)', card_line[3])
            hazard_dict = {'EN': [0, 0, 0],
                           'ST': [0, 0, 0],
                           'MY': [0, 0, 0],
                           'MA': [0, 0, 0]}
            for hazard in hazard_strings:
                hazard_dict[hazard[-2:]] = [int(x) for x in hazard[:-3].split("/")]
            self.hazards = hazard_dict
        else:
            self.hazards = None

        if "Avoids" in card_line[3]:
            mitigation_dict = {'EN': 0,
                               'ST': 0,
                               'MY': 0,
                               'MA': 0,
                               'Any': 0}
            if self.name != "Jack of All Trades" and self.name != "'Lucky' Dhorzan":
                mitigation_dict[card_line[3][9:11]] += int(card_line[3][7])
            elif self.name == "Jack of All Trades":
                mitigation_dict['Any'] = 2
            elif self.name == "'Lucky' Dhorzan":
                mitigation_dict['Any'] = 1
            self.mitigation = mitigation_dict
        else:
            self.mitigation = None
        if self.type == "Item":
            self.item_power = {1: {"Type": "", "Rule": ""},
                               2: {"Type": "", "Rule": ""},
                               3: {"Type": "", "Rule": ""}}
            self.item_sell_cost = [0, 0, 0]
            num_pat = re.compile(r'(?<![(/])(?!\))\d')
            try:
                self.item_upgrade_cost = int("".join(re.findall(num_pat, card_line[5])))
            except ValueError:
                self.item_upgrade_cost = None
            sell_costs = re.findall(r'\d+', card_line[6])
            if '1/2' in card_line[3]:
                line_three_depths = [1, 2]
                line_four_depths = [3]
            else:
                line_three_depths = [1]
                line_four_depths = [2, 3]
            if "Discard" in card_line[3]:
                for key in self.item_power.keys():
                    self.item_power[key]["Type"] = "Mitigate"
                first_effect = re.findall(r'(\d\s[A-Z][A-Z])', card_line[3])
                second_effect = re.findall(r'\d\s[A-Z][A-Z]', card_line[4])
            elif "Re-arrange" in card_line[3]:
                for key in self.item_power.keys():
                    self.item_power[key]["Type"] = "Scout"
                first_effect = re.findall(num_pat, card_line[3])
                second_effect = re.findall(num_pat, card_line[4])
            else:
                for key in self.item_power.keys():
                    self.item_power[key]["Type"] = "Shuffle"
                first_effect = second_effect = "Shuffle"
            for depth in line_three_depths:
                self.item_power[depth]["Rule"] = first_effect[0]
                self.item_sell_cost[depth - 1] = sell_costs[0]
            for depth in line_four_depths:
                self.item_power[depth]["Rule"] = second_effect[0]
                self.item_sell_cost[depth - 1] = sell_costs[1] if len(sell_costs) > 1 else sell_costs[0]
        else:
            self.item_power = None
            self.item_upgrade_cost = None
            self.item_sell_cost = None
        if card_line[1] == "Mission":
            mission_dict = {"Goal": card_line[3].split(" ")[0],
                            "Target": []}
            if 'Retrieve' in card_line[3]:
                ret_pat = re.compile(r'(?!Retrieve)(?!Delve)((\d|The)\s[A-Z]\w+(\s|\sof\s|\sof\sthe\s)([A-Z]\w+))')
                mission_dict["Target"].extend(re.findall(ret_pat, card_line[3] + card_line[4]))
                mission_dict["Target"] = [x[0] for x in mission_dict["Target"]]
            elif 'Defeat' in card_line[3]:
                mission_dict["Target"] = re.findall(r'(?!Defeat)[A-Z]\w+\s[A-Z]\w+', card_line[3])
            else:
                mission_dict["Target"] = ["The Living Darkness"]
            self.mission = mission_dict
        else:
            self.mission = None
        self.rules_string = "".join((card_line[3], card_line[4], card_line[5], card_line[6]))
        self.loyalty = card_line[7]
        try:
            self.cost = int(card_line[8][:-1])
        except ValueError:
            if self.type == "Expedition Leader":
                self.cost = 100
            else:
                self.cost = None
        self.back = card_line[9]
        self.layout = card_line[10]
        self.deck = card_line[11]
        if re.search(r'(\d\s[M|E|S][A|Y|N|T])', card_line[12]):
            ghost_strings = re.findall(r'\d\s[M|E|S][A|Y|N|T]', card_line[12])
            ghost_dict = {'EN': 0,
                          'ST': 0,
                          'MY': 0,
                          'MA': 0}
            for ghost in ghost_strings:
                ghost_dict[ghost[-2:]] = int(ghost[0])
            self.ghost = ghost_dict
            self.hazards = {key: [value] * 3 for key, value in ghost_dict.items()}
        else:
            self.ghost = None
        self.injured = False
        self.depth = 0
        depth_loot = card_line[3].split("/")
        self.card_dictionary = {
            "number": str(self.number).zfill(3),
            "name": self.name,
            "type": self.type,
            "game size": f"{self.game_size}+",
            "rewards": self.rewards,
            "hazards": self.hazards,
            "mitigation": str(self.mitigation),
            "item power": self.item_power,
            "item upgrade cost": self.item_upgrade_cost,
            "item sell cost": self.item_sell_cost,
            "mission": self.mission,
            "rules string": self.rules_string,
            "rules 1": card_line[3],
            "rules 2":  card_line[4],
            "rules 3": card_line[5],
            "rules 4": card_line[6],
            "treasure 1": depth_loot[0] if len(depth_loot) == 3 else None,
            "treasure 2": depth_loot[1] if len(depth_loot) == 3 else None,
            "treasure 3": depth_loot[2] if len(depth_loot) == 3 else None,
            "loyalty": self.loyalty,
            "cost": f"Cost: {self.cost} G",
            "back": self.back,
            "layout": self.layout,
            "deck": self.deck,
            "ghost": self.ghost
        }

    def view(self):
        view_string = f"{str(self.number).zfill(3)} {self.name}\n" \
                      f"Type: {self.type}\n" \
                      f"Players: {self.game_size}\n" \
                      f"Rules: {self.rules_string}\n" \
                      f"Loyalty: {self.loyalty if self.loyalty else 'N/A'}\n" \
                      f"Cost: {self.cost if self.cost else 'N/A'}\n" \
                      f"Back: {self.back}\n" \
                      f"Layout: {self.layout}\n" \
                      f"Deck: {self.deck}\n"
        return view_string

    def __repr__(self):
        return self.name


class Board:

    def __init__(self, decks):
        self.card_total = sum(len(x) for x in decks.values())
        self.dungeon = decks['Dungeon']
        # makes sure that 'The Darkness Hungers!' is always at the bottom of the deck.
        bottom_card = self.dungeon.pop(-1)
        shuffle(self.dungeon)
        self.dungeon.append(bottom_card)
        self.peons = []
        self.basics = []
        self.advanceds = []
        self.tavern = decks['Tavern']
        for index, card in enumerate(self.tavern):
            if card.type == "Peon":
                self.peons.append(self.tavern[index])
            if card.type == "Basic Adventurer":
                self.basics.append(self.tavern[index])
            if card.type == "Advanced Adventurer":
                self.advanceds.append(self.tavern[index])
        shuffle(self.peons)
        shuffle(self.basics)
        shuffle(self.advanceds)
        self.tavern = {"peons": self.peons,
                       "basics": self.basics,
                       "advanceds": self.advanceds
                       }
        self.missions = decks['Mission']
        shuffle(self.missions)
        self.leaders = decks['Leader']
        shuffle(self.leaders)
        self.artefacts = decks['Artefact']
        self.discard = []

    def clean_up(self, stacks=None):
        self.dungeon.extend(self.discard)
        if stacks:
            for stack in stacks:
                self.dungeon.extend(stack.cards)
        self.discard = []

    def view(self):
        view_string = 'Dungeon: '
        for index, dungeon in enumerate(self.dungeon):
            view_string += str(dungeon)
            view_string += ", " if index < len(self.dungeon) - 1 else ".\n"
        view_string += 'Tavern: '
        for index, tavern in enumerate(self.tavern):
            view_string += str(tavern)
            view_string += ", " if index < len(self.tavern) - 1 else ".\n"
        view_string += 'Missons: '
        for index, mission in enumerate(self.missions):
            view_string += str(mission)
            view_string += ", " if index < len(self.missions) - 1 else ".\n"
        view_string += 'Leaders: '
        for index, leader in enumerate(self.leaders):
            view_string += str(leader)
            view_string += ", " if index < len(self.leaders) - 1 else ".\n"
        return view_string

    def __repr__(self):
        return self.view()


class Player:

    def __init__(self, name, personality, height):
        self.name = name
        self.personality = personality
        self.height = height
        self.party = []
        self.items = []
        self.missions = []
        self.gold = 0
        self.escape_order = 0
        self.loot = []
        self.graveyard = []
        self.home_base = []
        self.party_stats()
        self.used_runecaller = None

    def tidy_up(self, game_state, table):
        table.board.dungeon.extend(self.graveyard)
        loot_total = 0
        for card in self.loot:
            if card.type == "Artefact":
                self.home_base.append(card)
            else:
                loot_total += card.rewards[game_state.delve_no - 1]
                table.board.dungeon.append(card)
        table.log.append(f"{self.name} sells {len(self.loot)} items and gains {loot_total} gold.")
        self.gold += loot_total
        self.graveyard = []
        self.loot = []
        return game_state, table

    def give_leader(self, leader):
        self.leader = leader
        self.party.append(leader)
        self.party_stats()

    def party_stats(self):
        self.loot_max = 0
        self.health = len(self.party)
        mitigation_dict = {'EN': 0,
                           'ST': 0,
                           'MY': 0,
                           'MA': 0,
                           'Any': 0}
        for card in self.party:
            self.loot_max += 2 if not card.injured else 1
            self.health += 1 if not card.injured else 0
            if card.mitigation:
                for type, amount in card.mitigation.items():
                    mitigation_dict[type] += amount
        self.mitigation = mitigation_dict
        if 'Fateweaver' in [x.name for x in self.party]:
            self.void_ceiling = 3
        elif 'Clairvoyant' in [x.name for x in self.party]:
            self.void_ceiling = 2
        else:
            self.void_ceiling = 1

    def loot_check(self):
        self.party_stats()
        if len(self.loot) <= self.loot_max:
            return False
        return True

    def escape_check(self):
        self.party_stats()
        if len(self.loot) == self.loot_max:
            return True
        return False

    def balance_loot(self, discard_list):
        self.loot.sort(key=lambda x: x.rewards)
        loot_check = self.loot_check()
        while loot_check and self.loot:
            discard_list.append(self.loot.pop(0))
            loot_check = self.loot_check()
        return discard_list

    def take_damage(self, damage):
        self.party.sort(key=lambda x: x.cost)
        counter = damage
        while counter > 0:
            for card in self.party:
                if not card.injured and damage > 0:
                    card.injured = True
                    damage -= 1
            for index, card in enumerate(self.party):
                if card.injured and not card.type == "Expedition Leader" and damage > 1:
                    self.graveyard.append(self.party.pop(index))
            counter -= 1

    def plunder(self, stack, game_state, table):
        cards = stack.cards.copy()
        discard_list = []
        hazards = stack.hazards
        for type, amount in self.mitigation.items():
            if type in hazards.keys():
                hazards[type] -= amount
        total_hazards = sum(hazards.values())
        if self.items:
            for item_index, item in enumerate(self.items):
                if item.item_power[game_state.delve_no]["Type"] == "Mitigate":
                    if hazards[item.item_power[game_state.delve_no]["Rule"][-2:]] > 0:
                        hazards[item.item_power[game_state.delve_no]["Rule"][-2:]] \
                            -= int(item.item_power[game_state.delve_no]["Rule"][0])
                        table.log.append(f"{self.name} used {item.name} to mitigate "
                                         f"{item.item_power[game_state.delve_no]['Rule']} damage.")
                        table.board.discard.append(self.items.pop(item_index))
        total_damage = 0
        for _ in range(total_hazards):
            d6_roll = randint(1, 6)
            if d6_roll >= 5:
                total_damage += 1
        table.log.append(f"{self.name} takes {total_damage} damage.")
        self.take_damage(total_damage)
        for card in cards:
            if card.type == "Null":
                discard_list.append(card)
            elif card.layout == "Treasure":
                self.loot.append(card)
            elif card.layout == "Hazard":
                self.graveyard.append(card)
            elif card.layout == "Item":
                self.items.append(card)
            elif card.layout == "Artefact":
                self.loot.append(card)
            discard_list = self.balance_loot(discard_list)
        table.log.append(f"{self.name} is forced to discard {discard_list}.")
        return stack, game_state, table, discard_list

    def final_score(self):
        artefect_price = 120 if self.leader == 'Ulgrim the Auctioneer' else 100
        final_gold = self.gold + (len(self.home_base) * artefect_price)
        return {'Name': self.name, 'Score': final_gold, 'Party': self.party}

    def view(self):
        view_string = f"{self.name}, {self.personality} personality, height: {self.height} cm\n" \
                      f"Party: {self.party}\n" \
                      f"Items: {self.items}\n" \
                      f"Loot: {self.loot}\n" \
                      f"Graveyard: {self.graveyard}\n" \
                      f"Missions: {self.missions}\n" \
                      f"Home base: {self.home_base}"
        return view_string

    def __repr__(self):
        return self.view()


class Table:

    def __init__(self, players, board):
        self.players = players
        self.board = board
        self.delve = 1
        self.log = []


class Stack:

    def __init__(self, card, delve):
        self.cards = [card]
        self.delve = delve
        self.update()

    def update(self):
        self.size = len(self.cards)
        self.rewards = 0
        self.hazards = {'EN': 0,
                        'ST': 0,
                        'MY': 0,
                        'MA': 0}
        self.total_hazards = 0
        for item in self.cards:
            if item and item.rewards:
                self.rewards += item.rewards[self.delve - 1]
            if item and item.hazards:
                for type, amount in self.hazards.items():
                    self.hazards[type] += item.hazards[type][self.delve - 1]
        self.total_hazards = sum(self.hazards.values())

    def clear(self):
        temp_cards = self.cards.copy()
        self.cards = []
        self.update()
        return temp_cards

    def view(self):
        view_string = '<'
        for index, card in enumerate(self.cards):
            try:
                view_string += card.name
            except AttributeError:
                view_string += 'None'
            view_string += ', ' if index < len(self.cards) - 1 else '>'
        return view_string

    def __repr__(self):
        return self.view()


class Game_state:

    def __init__(self, player_numbers, delve_no, bottom_card):
        self.player_number = player_numbers
        self.choosing_table = [True] * player_numbers
        self.exploring_table = [True] * player_numbers
        self.escape_table = [False] * player_numbers
        self.escape_number = 0
        self.approach_of_darkness = False
        self.to_draw = player_numbers
        self.delve_no = delve_no
        self.bottom_card = bottom_card
        self.current_player = None
