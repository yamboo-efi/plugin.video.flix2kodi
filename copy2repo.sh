#!/usr/bin/env bash
cp changelog.txt ../logi85.github.io/plugin.video.flix2kodi/
cp addon.xml ../logi85.github.io/plugin.video.flix2kodi/
cp icon.png ../logi85.github.io/plugin.video.flix2kodi/
cp fanart.jpg ../logi85.github.io/plugin.video.flix2kodi/
zip -r ../logi85.github.io/plugin.video.flix2kodi/plugin.video.flix2kodi-`python read_version.py`.zip . -x ./.git\* ./copy2repo.sh ./read_version.py ./test\* ./.git* ./.idea\*
cd ../logi85.github.io/
/usr/bin/python3 init.py
