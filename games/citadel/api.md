TODO: Swagger https://swagger.io/

## create_instance

TBD

## join

`POST join`
  - usename: str
  - token: str

### Success
```json
{
  "success": true,
  "message": null,
  "user_id": "1234"
}
```

### Invalid token
```json
{
  "success": false,
  "message": "Error message"
}
```

## players
Defines the players in the game. 

`GET players`
```json
{
  "token": ""
}
```
Returns the list of players associated to room with the given token.
```json
{
  "players": [
    {
      "username": "",
      "user_id": ""
    }
  ]
}
```

## Get Game state
Probably how the game looks is defined in the game settings.
If there is a deck and it has a "graveyard", it adds it in the interface.
This interface returns how the interface should look like:
- Number of interactive stuff,
- Is there a timer?
- Some basic design, like card backgrounds, ...

`GET game-state`
```json
{
  "token": ""
}
```

This should be updated continuously (so probably at every change, this will be pushed to the players), 
and should only give information that each user should have.

Returns: TBD

## Updating
Shows the item to everybody
`POST interaction`
 ```json
{
  "user_id": "id of the user who interacted",
  "token": "",
  "target": "The element the user has interacted with",
  "interaction": "a dictionary containing the information of the interaction."
}
```
The content of the interaction will vary depending on the target to suit the needs of each element.
For instance, picking a card from a deck should also give which one was taken, or how many...
They will correspond to the signature of the associated function on the server.

Returns the new state (as when calling `GET game-state`) and should also push a new state to all players.



