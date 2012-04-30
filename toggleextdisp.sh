#!/bin/bash

IN="LVDS1"
EXT="VGA1"
mode=640x480

while getopts 1234m: opt; do
    case "$opt" in
        1) mode=640x480;;
        2) mode=800x600;;
        3) mode=1024x768;;
        4) mode=1280x800;;
        m) mode=$OPTARG;;
        [?]) print >&2 "Usage: $0 [[-1|2|3|4] | [-m <horizontal_res>x<vertical_res>]]"
	    exit 1;;
	esac
done

# Create and add a mode to ext disp
# xrandr --newmode "1280x800"  83.50  1280 1352 1480 1680  800 803 809 83 -hsync +vsync
# xrandr --addmode VGA1 "1280x800"
# external and own monitors on auto, only if same preferred mode
# xrandr --output $IN --auto --output $EXT --auto
# external only
# xrandr --output $IN --off --output $EXT --auto
# zoom aroound and follow the cursor
# xrandr --output $IN --auto --output $EXT --pos 0x0 --panning 800x600+0+0/1280x800+0+0/64/64/64/64

if (xrandr | grep "$EXT" | grep "+") then
    xrandr --output $EXT --off --output $IN --auto
elif (xrandr | grep "$EXT" | grep " connected") then
    xrandr --output $IN --mode $mode --output $EXT --mode $mode
fi

