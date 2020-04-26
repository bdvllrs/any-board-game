from setuptools import find_packages, setup

setup(name='game-engine',
      version='0.1.0',
      install_requires=['PyYAML', 'aiohttp', 'numpy'],
      extras_require={
          'dev': [
              'pytest',
              'pytest-aiohttp'
          ]},
      packages=find_packages())
