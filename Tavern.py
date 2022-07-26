from random import shuffle


def tavern_phase(game_state, table):
    """This function contains the main game loop for the Tavern phase"""
    table.log.append(f"Tavern Phase, {game_state.delve_no}"
                     f"{'st' if game_state.delve_no == 1 else 'nd' if game_state.delve_no == 2 else 'rd'}"
                     f" turn.")
    tableau, table = create_tableau(game_state, table)
    table.players = tavern_order(table.players)
    table.log.append(f"Selection order: {[x.name for x in table.players]}")
    while any(game_state.choosing_table):
        for player_index, choosing in enumerate(game_state.choosing_table):
            if choosing:
                bought_item = False
                player = table.players[player_index]
                for index, card in enumerate(tableau):
                    if card.cost <= player.gold and not bought_item:
                        table.log.append(f"{player.name} bought {card.name} for {card.cost}")
                        player.party.append(tableau.pop(index))
                        player.gold -= (card.cost - 5 if player.leader == 'Thorgi Silvertongue' else - 0)
                        bought_item = True
                if not bought_item:
                    table.log.append(f"{player.name} passes.")
                    game_state.choosing_table[player_index] = False
                table.players[player_index] = player
    table.board.tavern = clean_up(table.board.tavern, tableau)
    table.log.append(f"{game_state.delve_no}"
                     f"{'st' if game_state.delve_no == 1 else 'nd' if game_state.delve_no == 2 else 'rd'}"
                     f" Tavern Phase ends.")
    game_state.choosing_table = [True for x in game_state.choosing_table]
    for index, player in enumerate(table.players):
        player.party_stats()
    return game_state, table


def create_tableau(game_state, table):
    """This function generates the tableaus for the tavern"""
    delve_dict = {1: (2, 1, 0), 2: (1, 1, 1), 3: (0, 2, 1)}
    peons = len(table.players) * delve_dict[game_state.delve_no][0]
    basics = len(table.players) * delve_dict[game_state.delve_no][1]
    advanceds = len(table.players) * delve_dict[game_state.delve_no][2]
    p_list = table.board.tavern['peons']
    b_list = table.board.tavern['basics']
    a_list = table.board.tavern['advanceds']
    shuffle(p_list)
    shuffle(b_list)
    shuffle(a_list)
    tableau = []
    for _ in range(peons):
        tableau.append(p_list.pop(0))
    for _ in range(basics):
        tableau.append(b_list.pop(0))
    for _ in range(advanceds):
        tableau.append(a_list.pop(0))
    shuffle(tableau)
    table.log.append(f"Set out a tavern containing {peons} peons, {basics} basic adventurers and {advanceds}"
                     f" advanced adventurers:\n {tableau}")
    return tableau, table


def clean_up(tavern, tableau):
    """tidies things up and returns the unpicked cards to the right decks"""
    peons = []
    basics = []
    advanceds = []
    for index, card in enumerate(tableau):
        if card.type == "Peon":
            peons.append(tableau.pop(index))
        if card.type == "Basic Adventurer":
            basics.append(tableau.pop(index))
        if card.type == "Advanced Adventurer":
            advanceds.append(tableau.pop(index))
    peons.extend(tavern['peons'])
    basics.extend(tavern['basics'])
    advanceds.extend(tavern['advanceds'])
    shuffle(peons)
    shuffle(basics)
    shuffle(advanceds)
    return {
            "peons": peons,
            "basics": basics,
            "advanceds": advanceds
            }


def tavern_order(players):
    """handles the tavern selection order, including breaking ties with height"""
    players.sort(key=lambda x: x.gold, reverse=True)
    max_gold = players[0].gold
    if sum(player.gold == max_gold for player in players) > 1:
        sub_list = []
        for index, player in enumerate(players):
            if player.gold == max_gold:
                sub_list.append(players.pop(index))
        sub_list.sort(key=lambda x: x.height, reverse=True)
        sub_list.extend(players)
        return sub_list.copy()
    return players.copy()
