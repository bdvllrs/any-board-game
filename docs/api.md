# :page_with_curl: API

## Some object definitions

### `gameId`
`str`, name of the game (unique).

### `playerId`
`uuid` unique id of a player

### `roundId`
`uuid` unique id of a round

### `GameDescription`
```
{
    "gameId": gameId,
    "rules": markdown,
    "description": str,
    "min_players": int,
    "max_players": int
}
```

### `RoundInformation`
```
{
  "playerId": playerId,
  "id": roundId,
  "gameId": gameId,
  "status": ("pending" | "started"),
  "createdOn": timestamp,
  "createdBy": str,
  "minPlayers": int,
  "maxPlayers": int,
  "public": bool,
  "players": list[str]
}
```

## `GET /game/list`
List the available games to play.

### Returns
`list[GameDescription]`

## `GET /game/<gameId>`
Returns information of a particular game.

### Returns
`GameDescription`

### Errors
- 404:  if `gameId` does not exist.

## `POST /round/create/<gameId>`
Create a new round of a given game.

### Form data
- `username` (str): username of the player
- `public` (bool, defaults to false): whether or not the round is visible by the public (if true, it will be listed in the round list).

### Returns
`RoundInformation`

### Errors
- 404 "Game does not exists.", `gameId` does not exist.
- 500 "An unexpected error has occurred. ...", an error occured loading and initializing the game. Check the `__init__` of the GameInstance.
- 403 "You cannot enter the game.", you do not fit the pre-requisite to enter the game (the `can_add_player` method of the GameInstance).

## `GET /round/{round_id}/join`
TODO
## `GET /round/list`
TODO
