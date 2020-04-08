TODO: Swagger https://swagger.io/
## Errors
If something is incorrect, the response will be:
```json
{
    "error": true,
    "message":  "Some error message"
}
```

## Create game instance

`POST /create`
- `game` in `['bataille']`:  Name of the game to create

### Success
```json
{
    "game_id": "the id of the new game",
    "error": false
}
```

## join

`POST /join`
  - game_id (str): game id of the game instance
  - username (str): username of the player
  - socket_id (str): socket.IO id of the user to add him to the game instance room.

### Success
```json
{
  "error": false,
  "message": "",
  "player_id": "id of the player. Is used for all interactions with the server.",
  "players": ["username 1", "username 2"],
  "state": {
      "nodes": [
          {
            "name": "node_name",
            "is_initial": "whether it is the initial state",
            "is_end": "whether it is the final state",
            "trigger": "type of trigger of the node. Either `CLIENT_ACTION` if state starts if the client calls the /play API, or null if started automatically.",
            "message_backbone": "The expected message backbone from the server when this node is triggered"
          }
      ],
      "edges": [
          {"node_start":  "node name", "node_end":  "node name"}
      ]
  }
}
```
### Message backbone
```json
{
    "message_backbone": {
      "some_key":  {"$IN":  ["available", "values"]}
    }
}
```
Example of expected message when calling the "/play" entry point:
```json
{
  "some_key": "available"
}
```

### new-player socket
A `new-player` named socket message will be emitted to all players in the room of the game instance with message:
```json
{
  "username": "new player username"
}
```

## Start game

`POST /start`
- game_id (str): id of the game instance
- player_id (str): id of the player starting the game. Any player who joined the game can start it.

### Success
```json
{
    "error": false,
    "message": "",
    "current_node_state": "name of the current node in the graph."
}
```


## Play game

`POST /play`
- game_id (str): id of the game instance
- player_id (str): id of the player starting the game. Any player who joined the game can start it.
- message (json): potential message to enter new node.

### Success
```json
{
    "error": false,
    "message": "",
    "current_node_state": "name of the current node in the graph."
}
```


## Chat
To send a chat message, send a named socket "emit_chat_message" with data:
```json
{
  "game_id": "id of the game",
  "player_id": "id of the player sending the message",
  "message": "Sent message"
}
```

The server will then emit to all players (including the sender) this named socket to the game instance room:
```json
{
  "username": "username of the player sending the message",
  "message": "message sent"
}
```
