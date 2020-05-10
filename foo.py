from game_engine.utils import games_folder

print(games_folder)
print(list(games_folder.iterdir()))
for folder in games_folder.iterdir():
    if folder.is_dir():
        print(folder)
        print(list(folder.iterdir()))
