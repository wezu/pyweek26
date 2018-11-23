# Chart of Flowrock

## A Pyweek 26 entry by wezu

You will need Python 3.x and Panda3D installed to run this game.

Panda3D can be installed using pip:

```
pip install -r requirements.txt
```
or
```
python -m pip install panda3d
```

To run the game type in:

```
python run_game.py
```


The game is a first person, cell based, dungeon crawling ... thing. You navigate (a) random level(s) using a flow-chart. The default controls are:
- A - left
- W - up/forward
- D - right
You can define your own controls by editing the options.prc file (it's a text file), there you can also set the resolution, sound and music volume.


## Gameplay Video:
https://youtu.be/UBvi4CwX8xo

## Troubleshooting:
I expect You will have some problems running the game. It's almost a PyWeek tradition:
- on windows, intel gpu:
Using shadows can crash the game, when asked in game if you want shadows answer no
- on linux
You will (probably) need to add (or uncomment ) 'gl-version 3 2' in the options.prc, else the shaders won't run
- on mac
If you open the .app you will get an error; go to System Preferences, Security and Privacy, click the lock, and click Open Anyway.
The game will only run in potato mod, use the app provided, some fixes may be missing from the source

## If all goes wrong...
The game has a 'potato mode' if you can't get it to run, you can set 'potato-mode 1' in options.prc to disable all shaders. It won't look good, but it should run on any system capable of rendering opengl 1.1


