import os

from setuptools import find_packages, setup


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


setup(name='any-board-game',
      version='0.1.0',
      install_requires=['PyYAML', 'aiohttp', 'numpy'],
      package_data={
          "": package_files("any_board_game/games")
      },
      extras_require={
          'dev': [
              'pytest',
              'pytest-aiohttp'
          ]},
      packages=find_packages())
