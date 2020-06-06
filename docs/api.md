# :page_with_curl: Http API

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

### `
RoundInformation`
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

### `SimpleRoundInformation`
```
{
  "id": roundId,
  "gameId": gameId,
  "started": bool,
  "createdOn": timestamp,
  "createdBy": str,
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

## `GET /round/<roundId>/join`
Join a round 

### Arguments
- username (str): player username

### Returns
`RoundInformation`

### Errors
- 404 "{roundId} is not a valid roundId", provided `roundId` is incorrect.
- 403 "Game has already started.", given `roundId` correspond to an already started game.
- 403 "Username {username} is already taken.", provided username is already taken by another player in the game.
- 403 "You cannot enter the game.", either too many players already in the round, or do not fit the pre-requisite to enter the game (the `can_add_player` method of the GameInstance).

## `GET /round/list`
List the *public* started round.

### Returns
`list[SimpleRoundInformation]`


## What to read next
The Http API is half of the communication with the server.

The rest is handled by the [websocket API](https://github.com/bdvllrs/any-board-game/blob/master/docs/websocket-api.md).
(Start the games, and other game communications.)