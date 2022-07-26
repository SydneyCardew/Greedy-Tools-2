from Game_Classes import Board
from Game_Classes import Table
from Game_Classes import Game_state
from datetime import datetime
import os
from Tavern import tavern_phase
from Tavern import tavern_order
from Delve import delve_phase
from Recovery import recovery_phase


def run_game(players, deck, log_path, game_number, zeroes):
    board = make_board(deck, players)
    table = Table(players, board)
    table = set_up(table)
    game_state = Game_state(len(table.players), 0, table.board.dungeon.pop(-1))
    table.log.append(f"Initialising game. {table.board.card_total} cards in play.")
    for x in range(3):
        game_state.delve_no += 1
        game_state, table = tavern_phase(game_state, table)
        game_state, table = delve_phase(game_state, table)
        game_state, table = recovery_phase(game_state, table)
    game_state, table = determine_winner(game_state, table)
    make_log(table, log_path, game_number, zeroes)


def make_board(deck, players):
    deck_dict = {}
    for card in deck:
        if card.game_size <= len(players):
            if card.deck in deck_dict:
                deck_dict[card.deck].append(card)
            else:
                deck_dict[card.deck] = [card]
    board = Board(deck_dict)
    return board


def set_up(table):
    for player in table.players:
        player.give_leader(table.board.leaders.pop(0))
        player.gold = 40 if str(player.leader) == "Lady Minewater" else 30
        player.missions.append(table.board.missions.pop(0))
    table.players = tavern_order(table.players)
    for order, player in enumerate(sorted(table.players, key=lambda x: x.height, reverse=True)):
        player.escape_order = order
    return table


def determine_winner(game_state, table):
    final_scores = []
    for player in table.players:
        final_scores.append(player.final_score())
    final_scores.sort(key=lambda x: x['Score'], reverse=True)
    final_score_string = 'The game is over.\n\n'
    positions = ('The Winner', 'Second Place', 'Third Place', 'Fourth Place', 'Fifth Place')
    for index, final_score in enumerate(final_scores):
        final_score_string += f"{final_score['Name']} is {positions[index]} with {final_score['Score']} gold.\n"
        final_score_string += f"{final_score['Party']}\n\n"
    table.log.append(final_score_string)
    return game_state, table


def make_log(table, log_path, game_number, zeroes):
    current_time = datetime.now()
    small_time = current_time.strftime("%H:%M:%S")
    with open(f"{log_path}\\Log {str(game_number).zfill(zeroes)}.txt", "w+") as log_file:
        log_file.write(f"Log {str(game_number).zfill(zeroes)} created by Greedy Sim Version 2 at {small_time}\n\n"
                       f"{len(table.players)} players.\n\n")
        for index, item in enumerate(table.log):
            log_file.write(f"{str(index + 1).zfill(len(str(len(table.log))))} - {item}\n\n")




