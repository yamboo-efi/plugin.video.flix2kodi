#!/bin/sh

HANDLE=`/usr/bin/xdotool search "Google Chrome"`

if [ "$1" = "close" ];
then
    CMD="alt+F4"
elif [ "$1" = "pause" ];
then
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
fi

/usr/bin/xdotool windowactivate --sync $HANDLE key $CMD
