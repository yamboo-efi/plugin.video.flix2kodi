#!/bin/sh

HANDLE=`/usr/bin/xdotool search "Google Chrome"`
HANDLED=0


if [ "$1" = "close" ];
then
    CMD="alt+F4"
elif [ "$1" = "pause" ];
then
    /usr/bin/xdotool windowactivate --sync $HANDLE mousemove 960 450
    sleep 0.2
    /usr/bin/xdotool windowactivate --sync $HANDLE click 1
    CMD="space"
elif [ "$1" = "backward" ];
then
    CMD="Left space"
elif [ "$1" = "down" ];
then
    CMD="Left Left space"
elif [ "$1" = "forward" ];
then
    CMD="Right space"
elif [ "$1" = "up" ];
then
    CMD="Right Right space"

elif [ "$1" = "toggle_lang0" ];
then
    /usr/bin/xdotool windowactivate --sync $HANDLE mousemove 960 540
    sleep 0.2
    /usr/bin/xdotool windowactivate --sync $HANDLE mousemove 1630 980
    sleep 0.2
    /usr/bin/xdotool windowactivate --sync $HANDLE mousemove 1430 835
    sleep 0.2
    /usr/bin/xdotool windowactivate --sync $HANDLE click 1
    HANDLED=1
elif [ "$1" = "toggle_lang1" ];
then
    /usr/bin/xdotool windowactivate --sync $HANDLE mousemove 960 540
    sleep 0.2
    /usr/bin/xdotool windowactivate --sync $HANDLE mousemove 1630 980
    sleep 0.2
    /usr/bin/xdotool windowactivate --sync $HANDLE mousemove 1430 875
    sleep 0.2
    /usr/bin/xdotool windowactivate --sync $HANDLE click 1
    HANDLED=1
elif [ "$1" = "toggle_sub0" ];
then
    /usr/bin/xdotool windowactivate --sync $HANDLE mousemove 960 540
    sleep 0.2
    /usr/bin/xdotool windowactivate --sync $HANDLE mousemove 1630 980
    sleep 0.2
    /usr/bin/xdotool windowactivate --sync $HANDLE mousemove 1630 835
    sleep 0.2
    /usr/bin/xdotool windowactivate --sync $HANDLE click 1
    HANDLED=1
elif [ "$1" = "toggle_sub1" ];
then
    /usr/bin/xdotool windowactivate --sync $HANDLE mousemove 960 540
    sleep 0.2
    /usr/bin/xdotool windowactivate --sync $HANDLE mousemove 1630 980
    sleep 0.2
    /usr/bin/xdotool windowactivate --sync $HANDLE mousemove 1630 875
    sleep 0.2
    /usr/bin/xdotool windowactivate --sync $HANDLE click 1
    HANDLED=1
fi

if [ $HANDLED -eq 0 ];
then
    /usr/bin/xdotool windowactivate --sync $HANDLE key $CMD
fi