#Panda3D setup file
#For a list of all config options see:
#https://www.panda3d.org/manual/index.php/List_of_All_Config_Variables

#resolution, size of the game window in pixels
#the game can be resized by just resizing the game window
win-size 1280 720

#vertical sync 0=off, 1=on
#limit the fps to your monitor refresh rate, may help with tearing
sync-video 1

#in game frame rate meter 0=off 1=on
show-frame-rate-meter 0

#keyboard setup, default to W-A-(S)-D, only without the S, no going back
#see https://www.panda3d.org/manual/index.php/Keyboard_Support for special key names
left-key a
right-key d
up-key w

#sound volume 0.0 =off 1.0=max
sound-volume 0.75
#music volume 0.0 =off 1.0=max
music-volume 0.5

#on linux using intel drivers un-commenting this line may help run the game
#...it will also disable clipping on the flow-chart, and that may look funny
#gl-version 3 2

# potato mode = disables all shaders
#set it to 1 if you have problems running the game
potato-mode 0
