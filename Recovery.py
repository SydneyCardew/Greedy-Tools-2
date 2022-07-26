

def recovery_phase(game_state, table):
    table.log.append(f"Recovery Phase, {game_state.delve_no}"
                     f"{'st' if game_state.delve_no == 1 else 'nd' if game_state.delve_no == 2 else 'rd'}"
                     f" turn.")
    for player in table.players:
        game_state, table = player.tidy_up(game_state, table)
    game_state, table = check_missions(game_state, table)
    return game_state, table


def check_missions(game_state, table):
    for player in table.players:
        for mission in player.missions:
            pass
    return game_state, table
