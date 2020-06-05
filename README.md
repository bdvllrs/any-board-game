<div align="center">
<h1><code>any-board-game-server</code> :game_die:</h1>
</div>

## About
:warning: This is a work in progress...

Quickly build online multi-player board games.

Try our project on [our website](https://cards.busy.ovh).

This is the server side of the project!

## :computer: Client
- In rust: https://github.com/totorigolo/cards-client-rs

## :rocket: Quick Start
### Install

From our git repository:
```
pip install --user git+https://github.com/bdvllrs/any-board-game.git
```

Then start the server with:
```
abg-server [--port, -p SERVER_PORT]
```

### Add some games
If you are tired of the sample games provided with this repository, you can
add games created by others or yourself to your game collection.
You need to create a game folder when you will put your abg games.
You can then give a game folder to the `abg-server` command.

```
mkdir /path/to/abg_collection

abg-server --game_folder /path/to/abg_collection
```


## :green_book: Doc
- [API](https://github.com/bdvllrs/any-board-game/blob/master/docs/api.md)
