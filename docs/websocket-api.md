# :electric_plug: Websocket API

This assumes that you have read the [http API](https://github.com/bdvllrs/any-board-game/blob/master/docs/api.md).

Once a player has joined a round with the `GET /round/<roundId>/join`, the connexion can
be transformed into a socket connexion. 

The query argument `playerId` must be provided.

This socket connexion is how the server and the clients
will communicate during the game.

The message sent threw the websocket are json objects, always containing a `type`
key. The `type` defines the kind of message is sent to the server or client.

The following doc, the messages are titled by the `type` value of the message.

Moreover, we will denote by "connected players" all players connected that started
this websocket connexion on the same `roundId`.

## Some object definitions

### `componentId`
`str` id of a component.

### `componentType`
`str` type of component.
See [Game Components](https://github.com/bdvllrs/any-board-game/blob/master/docs/components.md)
for more information.

### `Action`
```
{
    "type": ("OnClick"),
    "target_component": componentId
}
```

For the moment, only a `OnClick` type is defined.

See [Client actions](https://github.com/bdvllrs/any-board-game/blob/master/docs/actions.md)
for more information.

### `Component`
```
{
    "type": componentType,
    "param1": "key1",
    ...
}
```

See [Game Components](https://github.com/bdvllrs/any-board-game/blob/master/docs/components.md)
for more informations.

### `ComponentDescription`
```
{
    "type": ("Create" | "Update" | "Delete"),
    "id": componentId,
    "component": Component
}
```
Note: there is no "component" key for type "Delete".

### `ComponentAppearance`
```
{
    "id": componentId,
    "position": ("top" | "left" | "right" | "bottom)
}
```

To do (this needs more refinement!)

## Messages from the *server*

### `PLAYER_CONNECTED`
Whenever a player connects to this websocket, this message is sent to all connected players of the round.

#### Message
```
{
    "type": "PLAYER_CONNECTED", 
    "username": str,
    "message": "Say hello to {username}."
}
```

### `PLAYER_DISCONNECTED`
Received when a connexion is closed with a player.

#### Message
```
{
    "type": "PLAYER_DISCONNECTED", 
    "username": str,
}
```

### `GAME_STARTED`
Received whenever the player that initiated the game started the game.
No new player will be able to join.

#### Message
```json
{"type": "GAME_STARTED"}
```

### `CHAT`
Chat message from a connected player.
#### Message
```
{
    "type": "CHAT",
    "message": "sent message",
    "author": "username of the author of the message"
}
```

### `NOTIFICATION`
A notification from the game.

#### Message
```
{
    "type": 'NOTIFICATION',
    "level": ("info" | "warning" | "error"),
    "duration": int (sec),
    "content": str
}
```

### `COMPONENTS_UPDATES`
Sends information on the components that needs to be displayed on the 
interface.

This message only inform on the components, not on how (and if) the element are displayed.
This is the goal of the `INTERFACE_UPDATE` message. However, it gives information
on how to display it.

There are 3 types of `COMPONENTS_UDPATES` event: 
- `Create` whenever a new component is added
- `Update` whenever a component is changed
- `Delete` whenever a component is no longer required.

Note: whenever an `Update` `COMPONENTS_UPDATES` message is sent, the interface
**should be** changed to display the new information.

#### Message
```
{
  "type": "COMPONENTS_UPDATES",
  "components": [ComponentDescription]
}
```

### `INTERFACE_UPDATE`
This message sends information on how to display the components sent via the
`COMPONENTS_UPDATES` message.

#### Message
```
{
    "type": "INTERFACE_UPDATE,
    "components": [ComponentAppearance]
}
```

### `ACTION_AWAITED`
Notify the client that an action of the player is required.

See [Client actions](https://github.com/bdvllrs/any-board-game/blob/master/docs/actions.md)
for more information.

#### Message
```
{
    "type": "ACTION_AWAITED,
    "all_of": [Action]
}
```

## Messages from the *client*

### `CLOSE`
Close the connexion. The server will then alert the other connected players
with a `PLAYER_DISCONNECTED` typed message.

#### Message example
```json
{"type": "CLOSE"}
```

### `PING`
The server will reply with a `{"type": "PONG"}` message.

### `START_GAME`
Start a pending game. Only the player that initiated the round can
successfully send this message (player in `createdBy` on a `RoundInformation`).

The server will then send a `GAME_STARTED` message to all connected players.

#### Message example
```json
{"type": "START_GAME"}
```

### `CHAT`
Send a `CHAT` message to all connected players.

#### Message example
```json
{
  "type": "CHAT",
  "message": "message content"
}
```

### `ACTION_RESPONSE`
Response after receiving a `ACTION_AWAITED` message. Sends 
action choices of the player.

### Message example
```
{
  "type": "ACTION_RESPONSE",  
  idComponent: actionResponse, 
  idComponent: actionResponse,
  ...
}
```
Where for each requested action from the server:
- `idComponent` corresponds to the component id from the `Action`
- `actionResponse` is the actionResponse of the component. (for example, a CardDeck will return the `componentId` of the card clicked by the player).

### `GET_COMPONENTS`
Asks the server to send the required components. The client will
then receive a `COMPONENTS_UPDATES` message.

#### Message examples

To get all components:
```json
{
  "type": "GET_COMPONENTS"
}
```

To ask for updates on specific component ids:
```json
{
  "type": "GET_COMPONENTS",
  "ids": ["id1", "id2"]
}
```

The response are `COMPONENTS_UPDATES` of types either `Update` or `Delete` (if the component no longer exists).

### `AWAITED_ACTIONS`
Asks the server to resend the last `ACTION_AWAITED` message.

#### Message example
```json
{
  "type": "AWAITED_ACTIONS"
}
```


