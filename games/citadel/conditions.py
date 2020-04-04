def pick_card_condition(node, env):
    return len(env['seen_players']) < len(env.players)


def start_used_power_condition(node, env):
    return True


def start_picked_coin_condition(node, env):
    return True


def used_power_picked_coin_condition(node, env):
    return True


def used_power_drew_card_condition(node, env):
    return True


def picked_coin_used_power_condition(node, env):
    return True


def picked_coin_built_condition(node, env):
    return True


def drew_card_used_power_condition(node, env):
    return True


def drew_card_built_condition(node, env):
    return True


def built_used_power_condition(node, env):
    return True


def playing_end_playing_start_condition(node, env):
    return True


def building_selection_start_condition(node, env):
    return True
