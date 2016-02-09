#!/bin/bash

# copy from https://github.com/andrewleech/plugin.video.netflixbmc/blob/master/browser.sh

# Managed to resolve the issues with, but will leave this here anyway, as its a good fallback
CHROME_STARTED=`ps -ef | grep chromium-browser | grep -v "grep" | wc -l`
if [ $CHROME_STARTED -gt 0 ]; then
        exit 1;
fi

# lets find out if xdotool actually exist before we try to call them.
command -v xdotool >/dev/null 2>&1
XDOTOOL=$?

url=$1

# notice the ampersand to send google chrome into back ground so that the script continues and we execute the xdotool below
/usr/bin/chromium-browser --start-maximized --disable-translate --disable-new-tab-first-run --no-default-browser-check --no-first-run --kiosk "$url" &
CHROME_PID=$!

if [ $XDOTOOL -eq 0 ]; then
        # no point sleeping if xdotool is not installed.
        sleep 5
        xdotool mousemove 9999 9999 click 1
else
        echo "xdotool is not installed, can't remove cursor"
fi
# wait for google-chrome to be killed 
wait $CHROME_PID

