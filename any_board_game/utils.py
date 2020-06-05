from pathlib import Path

sample_game_folder = Path(__file__).resolve().parents[1] / 'sample_games'

if __name__ == '__main__':
    print(sample_game_folder)
    print(list(sample_game_folder.iterdir()))
