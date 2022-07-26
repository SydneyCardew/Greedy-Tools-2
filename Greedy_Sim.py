import Card_Maker
import os
from datetime import date
import Game_Functions as gf
from Game_Classes import Player
from random import randint


def main():
    player_no = 4
    player_names = ('Alice', 'Bob', 'Carol', 'Dan', 'Erin')
    times_through = 100
    zeroes = len(str(times_through))
    today = str(date.today())
    log_path = os.getcwd() + f"\\Logs\\Greedy Sim Logs - {today}"
    incrementer = 1
    while os.path.exists(f"{log_path} - {str(incrementer).zfill(3)}"):
        incrementer += 1
    os.mkdir(f"{log_path} - {str(incrementer).zfill(3)}")
    log_path = log_path + f" - {str(incrementer).zfill(3)}"
    for game_number in range(times_through):
        deck = Card_Maker.make_deck()
        players = []
        for x in range(player_no):
            players.append(Player(player_names[x], 'default', randint(120, 201)))
        gf.run_game(players, deck, log_path, game_number + 1, zeroes)


if __name__ == "__main__":
    main()


