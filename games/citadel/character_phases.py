def action_phase(player, state):
    character_name = player.hand['character'][0].title.lower()

    if character_name == "assassin":
        assassin_phase(player, state)
    elif character_name == "voleur":
        voleur_phase(player, state)
    elif character_name == "magicien":
        # This is an asynchronous action.
        # It will add a button on the interface but the function is executed only if the button is pressed.
        state.env.interface.for_players([player]).add_button("Exchange cards with player.",
                                                             magicien_exchange_cards_player)
        state.env.interface.for_players([player]).add_button("Exchange cards with deck.",
                                                             magicien_exchange_cards_deck)
    elif character_name == "roi":
        roi_phase(player, state)
    elif character_name == "évèque":
        eveque_phase(player, state)
    elif character_name == "marchand":
        marchand_phase(player, state)
    elif character_name == "architecte":
        architecte_phase(player, state)
    elif character_name == "condottiere":
        condottiere_phase(player, state)

    # This blocks the automaton here, until this button is pressed.
    state.env.interface.for_players([player]).add_blocking_button("Finish turn.")


def assassin_phase(player, state):
    """
    Asks to pick a card from the character cards and kills this character.
    """
    cards = state.env.card_decks['character'].all()
    # This will ask the player to do an action right away.
    chosen_character = player.choose_card(cards)
    for player in state.env.players.all():
        if player.hand['character'][0].title == chosen_character.title:
            player.state['killed'] = True
            break


def voleur_phase(player, state):
    """
    Asks to pick a card from character cards and steals the money from that character.
    """
    cards = state.env.card_decks['character'].all()
    chosen_character = player.choose_card(cards)
    for player in state.env.players.all():
        if player.hand['character'][0].title == chosen_character.title:
            player.state['stolen'] = True
            break


def magicien_exchange_cards_player(player, state):
    pass


def magicien_exchange_cards_deck(player, state):
    pass


def roi_phase(player, state):
    player.state['king'] = True


def eveque_phase(player, state):
    pass


def marchand_phase(player, state):
    pass


def architecte_phase(player, state):
    pass


def condottiere_phase(player, state):
    pass
