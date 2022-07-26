from Game_Classes import Stack
from Game_Classes import Game_state
from random import shuffle
from random import choice
import time


def delve_phase(game_state, table):
    table.log.append(f"Expedition Phase, {game_state.delve_no}"
                     f"{'st' if game_state.delve_no == 1 else 'nd' if game_state.delve_no == 2 else 'rd'}"
                     f" turn.")
    stacks = []
    for player in table.players:
        if player.leader == 'Runecaller Svadi':
            player.used_runecaller = False
    for _ in table.players:
        drawn_card, table = draw_card(table)
        stacks.append(Stack(drawn_card, game_state.delve_no))
    if game_state.delve_no == 1:
        artefact_transfer = [table.board.artefacts[0]]
        table.board.artefacts = table.board.artefacts[1:]
        table.board.dungeon.extend(artefact_transfer)
        table.log.append(f"1 Artefact added to Dungeon.")
    elif game_state.delve_no == 2:
        artefact_transfer = table.board.artefacts[:2]
        table.board.artefacts = table.board.artefacts[2:]
        table.board.dungeon.extend(artefact_transfer)
        table.log.append(f"2 Artefacts added to Dungeon.")
    elif game_state.delve_no == 3:
        table.board.dungeon.extend(table.board.artefacts)
        table.log.append(f"6 Artefacts added to Dungeon.")
    table.log.append(f"{len(stacks)} stacks created: {stacks}")
    table.players.sort(key=lambda x: x.escape_order)
    table.log.append(f"Selection order: {[x.name for x in table.players]}")
    while any(game_state.exploring_table):
        for player_index, exploring in enumerate(game_state.exploring_table):
            game_state.current_player = table.players[player_index]
            if exploring:
                game_state, table, stacks = void(game_state, table, stacks)
                exploring = game_state.exploring_table[player_index]
            if exploring:
                game_state, table, stacks = explore(game_state, table, stacks)
                exploring = game_state.exploring_table[player_index]
            if exploring:
                game_state, table, stacks = take(game_state, table, stacks)
                exploring = game_state.exploring_table[player_index]
            table.players[player_index] = game_state.current_player
        for player_index, exploring in enumerate(game_state.exploring_table):
            if exploring:
                escape_check = table.players[player_index].escape_check()
                if escape_check:
                    game_state, table = escape_sequence(player_index, game_state, table)
    game_state.escape_number = 0
    table.board.clean_up(stacks)
    game_state.exploring_table = [True for x in game_state.exploring_table]
    game_state.approach_of_darkness = False
    return game_state, table


def draw_card(table):
    if table.board.dungeon:
        drawn_card = table.board.dungeon.pop(0)
        return drawn_card, table
    return None, table


def void(game_state, table, stacks):
    possible_voids = []

    for index, stack in enumerate(stacks):
        if stack.size <= game_state.current_player.void_ceiling and stack.total_hazards > 0:
            possible_voids.append(index)
        elif stack.size > 3 and game_state.current_player.leader == 'Runecaller Svadi' and stack.total_hazards > 5:
            possible_voids.append(index)
            game_state.current_player.used_runecaller = True
    if possible_voids:
        void_choice = choice(possible_voids)
        table.log.append(f"{game_state.current_player.name} voids a stack of {stacks[void_choice].size}.")
        table.board.discard.extend(stacks[void_choice].clear())
    for stack in stacks:
        stack.update()
    return game_state, table, stacks


def explore(game_state, table, stacks):
    for stack in stacks:
        drawn_card, table = draw_card(table)
        if not drawn_card:
            if not game_state.approach_of_darkness:
                table.log.append(f"The Darkness Approaches!")
                table.board.clean_up()
                drawn_card, table = draw_card(table)
                game_state.approach_of_darkness = True
            else:
                table.log.append(f"Darkness overwhelms the remaining adventurers.")
                for index, exploring in enumerate(game_state.exploring_table):
                    if exploring:
                        table.players[index].escape_order = game_state.escape_number
                        game_state.escape_number += 1
                game_state.exploring_table = [False for x in game_state.exploring_table]
                return game_state, table, stacks
        placed_card = False
        for stack in stacks:
            if stack.size == min([x.size for x in stacks]) and not placed_card:
                stack.cards.append(drawn_card)
                stack.update()
                placed_card = True

    return game_state, table, stacks


def take(game_state, table, stacks):
    must_take = False
    if max([x.size for x in stacks]) >= 6:
        # currently selects the stack to take at random
        shuffle(stacks)
        taken = False
        for stack in stacks:
            if stack.size >= 6 and not taken:
                table.log.append(f"{game_state.current_player.name} is forced to take a stack of {stack.size} cards:"
                                 f" {stack.cards}")
                stack, game_state, table, discard_list = game_state.current_player.plunder(stack, game_state, table)
                table.board.discard.extend(discard_list)
                stack.clear()
                taken = True
    elif max([x.size for x in stacks]) >= 3:
        # also at random. Eventually these will have very different logic.
        shuffle(stacks)
        taken = False
        for stack in stacks:
            if stack.size >= 3 and stack.rewards > stack.total_hazards * 10 and not taken:
                table.log.append(f"{game_state.current_player.name} chooses to take a stack of {stack.size} cards:"
                                 f"{stack.cards}")
                stack, game_state, table, discard_list = game_state.current_player.plunder(stack, game_state, table)
                table.board.discard.extend(discard_list)
                stack.clear()
                taken = True
    else:
        pass
    return game_state, table, stacks


def escape_sequence(player_index, game_state, table):
    table.log.append(f"{table.players[player_index].name} is escaping the dungeon!")
    game_state.exploring_table[player_index] = False
    sequence_length = len(table.players[player_index].loot)
    while sequence_length > 0:
        drawn_card, table = draw_card(table)
        if not drawn_card:
            if not game_state.approach_of_darkness:
                table.log.append(f"The Darkness Approaches!")
                table.board.clean_up()
                drawn_card, table = draw_card(table)
                game_state.approach_of_darkness = True
            else:
                table.log.append(f"Darkness overwhelms the remaining adventurers.")
                for index, exploring in enumerate(game_state.exploring_table):
                    if exploring:
                        table.players[index].escape_order = game_state.escape_number
                        game_state.escape_number += 1
                game_state.exploring_table = [False for x in game_state.exploring_table]
                return game_state, table
        stack, game_state, table, discard_list =\
            table.players[player_index].plunder(Stack(drawn_card, game_state.delve_no), game_state, table)
        table.board.dungeon.extend(discard_list)
        sequence_length -= 1
    return game_state, table
