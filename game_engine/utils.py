from pathlib import Path

games_folder = Path(__file__).resolve().parent / 'games'

if __name__ == '__main__':
    print(games_folder)
