from setuptools import find_packages, setup

setup(name='game-engine',
      version='0.1.0',
      install_requires=['PyYAML', 'flask==1.1.0', 'flask-socketio'],
      packages=find_packages())
