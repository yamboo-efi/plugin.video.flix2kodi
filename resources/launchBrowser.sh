#!/bin/bash

# copy from https://github.com/andrewleech/plugin.video.netflixbmc/blob/master/browser.sh

# Managed to resolve the issues with, but will leave this here anyway, as its a good fallback
CHROME_STARTED=`ps -ef | grep google-chrome | grep -v "grep" | wc -l`
if [ $CHROME_STARTED -gt 0 ]; then
        exit 1;
fi

# lets find out if irxevent and xdotool actually exist before we try to call them.
command -v irxevent >/dev/null 2>&1
IRXEVENT=$?
command -v xdotool >/dev/null 2>&1
XDOTOOL=$?

if [ $IRXEVENT -eq 0 ]; then
        killall irxevent >/dev/null 2>&1
fi

# http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-stored-in
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

url=$1

# notice the ampersand to send google chrome into back ground so that the script continues and we execute the xdotool below
/usr/bin/google-chrome --start-maximized --disable-translate --disable-new-tab-first-run --no-default-browser-check --no-first-run --kiosk "$url" &
CHROME_PID=$!

if [ $IRXEVENT -eq 0 ]; then
        # run irxevent as a daemon so that we can call xdotool
        irxevent -d $DIR/netflix.lirc &
else
        echo "irxevent is not installed, can't do remote control"
fi

if [ $XDOTOOL -eq 0 ]; then
        # no point sleeping if xdotool is not installed.
        sleep 5
        xdotool mousemove 9999 9999 click 1
else
        echo "xdotool is not installed, can't remove cursor"
fi
# wait for google-chrome to be killed before killing irxevent below.  This only works if we execute irxevent as a daemon, otherwise
# the script would never finish.
wait $CHROME_PID

if [ $IRXEVENT -eq 0 ]; then
        killall irxevent >/dev/null 2>&1
fi
