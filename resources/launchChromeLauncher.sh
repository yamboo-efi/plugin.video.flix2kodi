#!/bin/bash
for i in $@; do :; done
x="$i --kiosk"
/usr/bin/kodi-send -a "RunAddon(browser.chromium, $x)" &
exit 0