# Round WebSocket protocol

When a `GET /round/{roundId}/join` request succeeds, the socket will be upgraded
by the server to a WebSocket. This document documents the API that shall be
followed by the client and the server.

The messages are represented as JSON strings. The messages are internally tagged
using the attribute named `type`. For instance, a message of type `Foo` with two
attributes, `id` and `data`, is to be represented as:

```json
{"type": "Foo", "id": 123, "data": "bar"}
```

## Type aliases

- `Username -> string`
- `CardId -> u64`
- `Url -> string`

## Objects

### Player

- `username: string`

#### Example
```json
{"type": "Player", "username": "la_carte"}
```

### Card

- `card_id: CardId`
- `title: string`
- `description: string`
- `front_image: Url`
- `back_image: Url`

## Messages

Messages can be sent from both the client and the server.

### [server->client] player_info_update

- `username: string`
- `coins: u64`
- `dices: array Dice`

### [server->client] interface_add

### [server->client] interface_remove

### [server->client] interface_update

### [server->client] update_interface

TODO
* Hands
* Boards (later)
* Scoreboard
* Dice
* Timer

hands:
  - player_id: u64
    cards:
      - u64
      - u64
      - u64
  - player_id: u64

### [server->client] set_player_hand

- `player_id: u64`
- `cards: array CardId`
