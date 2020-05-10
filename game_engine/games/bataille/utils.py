from game_engine.games.bataille.response_validations import PlayResponseValidator


async def new_turn_setup(node):
    # This method sets up a new turn.
    # You can access the GameEnv instance with node.env
    # First, we will define the played cards of this turn by an empty dict
    assert len(node.env.state['played_cards']) == 0, "Played cards should be empty"
    # Then we define the order of play
    players = list(node.env.players.keys())
    # the first player in the previous turn will be last to play
    players = players[1:] + [players[0]]
    # And we add it to the state
    node.env.state['player_order'] = players
    node.env.state['played_card_to_player'] = dict()
    node.env.state['current_player'] = node.env.state['player_order'][0]


async def play_node_setup(node):
    # Now we update the order of play and current player
    node.env.state['current_player'] = node.env.state['player_order'].pop(0)
    # We will use this setup to block the automaton and wait for a player response.
    # First, the get the player whose turn it is
    player_uid = node.env.state['current_player']
    player = node.env.players[player_uid]
    # We will now await a response from that player
    # Note that we added a validator. This will then wait for a specific response from the client.
    # This validator checks that the given card is owned by the player
    response = await player.client_action({
        "all_of": [{
            "type": "OnClick",
            "target_component": "hand"
        }]
    }, validators=[PlayResponseValidator(node)])

    card = response['hand']  # This is a Card object

    node.env.state['played_card_to_player'][card.name] = player_uid
    node.env.state['played_cards'].add([card])
    # And we remove the card from the hand of the player.
    node.env.state['hands'][player.uid].remove(card)
    # Now we update the played cards in the


async def new_turn_end_condition(node):
    # We go the end node if someone has played all his cards
    for player_uid in node.env.players:
        hand = node.env.state['hands'][player_uid]
        if not len(hand):
            return True
    return False


async def play_new_turn_condition(node):
    # We do a new turn if the player_order list is empty.
    if not len(node.env.state['player_order']):
        return True
    return False


async def set_player_in_node_state_action(node, next_node):
    """
    Adds the next playing player in the new node state.
    """
    next_node.state['player'] = node.env.state['current_player']


async def play_new_turn_action(node, next_node):
    # If we do a new turn, we need to find who won the turn
    card_order = sorted(node.env.state['played_cards'])
    loser_card = card_order[0]  # the one with lowest card loses and gets the cards of all other players
    loser = node.env.state['played_card_to_player'][loser_card.name]
    node.env.state['hands'][loser].add(node.env.state['played_cards'].pop(n='all'))


async def new_turn_end_action(node, next_node):
    # Set the winner
    for player_uid, player in node.env.players.items():
        hand = node.env.state['hands'][player_uid]
        if not len(hand):
            node.env.add_winner(player)
