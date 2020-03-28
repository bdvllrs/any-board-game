from game_engine.cards import CardDeck
from game_engine.environment import GameEnvironment, GamePhase
from game_engine.players import PlayerManager
from game_engine.state import GameState


def selection_phase(state):
    # state is already a copy, we can modify it without remorse :)
    # Start by setting all cards to available
    for card in state.env.card_decks['character'].from_states(['discarded', 'selected']).all():
        card.to_state('available')

    # Setup of the phase
    state.env.card_decks['character'].shuffle()
    state.env.card_decks['character'].from_state('available').pick(1)[0].to_state('discarded')

    # Set the first player by the player with king state
    first_player = None
    for player in state.env.players.all():
        if player.has_state('king'):
            first_player = player
            break

    assert first_player is not None, "There is not king..."

    # Give turns to the players
    for player in state.env.players.all(first=first_player):
        random_card = state.env.card_decks['character'].from_state('available').pick(1)[0]
        player.hand['character'].append(random_card)
        random_card.to_state('selected')

    state.set_next_phase('building')
    return state


def building_phase(state):
    card_to_player = dict()
    # First, we define which player has which character.
    for player in state.env.players.all():
        # Remove old states
        del player.state['killed']
        del player.state['stolen']

        character_name = player.hand['character'][0].title
        card_to_player[character_name.lower()] = player

    # Then we define the order of playing
    order = ['assassin', 'voleur', 'magicien', 'roi', 'évèque', 'marchand', 'architecte', 'condottiere']
    order = [card_to_player[character_name] for character_name in order]

    number_max_buildings = 0
    thief_player = None

    for player in state.env.players.all(order=order):
        if player.hand['character'][0].title.lower() == "voleur":
            thief_player = player
        if 'killed' in player.state:
            state.env.interface.send_message(f"The {player.hand['character'][0].title} has been killed!")
            continue
        if 'stolen' in player.state:
            assert thief_player is not None
            state.env.interface.send_message(f"The {player.hand['character'][0].title} has been stolen!")
            money_player = player.state['money']
            player.state['money'] = 0
            thief_player.state['money'] += money_player
            continue
        state.env.interface.send_message(f"The {player.hand['character'][0].title} is playing! \n"
                                         "It's {player.username}!")
        new_player_state = player.play()  # Play and creates a new state
        state.update_from_player_state(new_player_state)  # Update the global state
        num_built_buildings = len(player.state['built_buildings'])
        if num_built_buildings > number_max_buildings:
            number_max_buildings = num_built_buildings

    if number_max_buildings == 8:  # End of the game
        state.set_next_phase('end')
    else:
        state.set_next_phase('selection')
    return state


def end_phase(state):
    player_points = [(player, player.state['points']) for player in state.env.players.all()]
    # Sort players by number of points
    sorted_players = sorted(player_points, key=lambda x: x[1], reverse=True)
    winners = []
    # Select all players with highest score as winner
    for player, points in sorted_players:
        if not len(winners) or points == winners[0].state['points']:
            winners.append(player)
    # Set winners in the state
    state.set_winners(winners)
    # Send end game event.
    state.end_game()
    return state


if __name__ == '__main__':
    # Define the prototypes of the players
    players = PlayerManager(min_players=4, max_players=7)

    card_decks = dict(character=CardDeck(from_yaml="character_cards.yaml"),
                      building=CardDeck(from_yaml="building_cards.yaml"))

    phases = dict(selection=GamePhase(selection_phase),
                  building=GamePhase(building_phase),
                  end=GamePhase(end_phase))

    game_env = GameEnvironment(players,
                               card_decks=card_decks)

    game_state = GameState(players, phases)
    game_state.set_next_phase('selection')
