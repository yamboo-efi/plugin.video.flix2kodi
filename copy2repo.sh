#!/usr/bin/env bash
cp changelog.txt ../logi85.github.io/plugin.video.flix2kodi/
cp addon.xml ../logi85.github.io/plugin.video.flix2kodi/
cp icon.png ../logi85.github.io/plugin.video.flix2kodi/
cp fanart.jpg ../logi85.github.io/plugin.video.flix2kodi/
cd `pwd`/..
VERSION=`python plugin.video.flix2kodi/read_version.py|tr -d '\r'`
zip -r logi85.github.io/plugin.video.flix2kodi/plugin.video.flix2kodi-$VERSION.zip plugin.video.flix2kodi -x plugin.video.flix2kodi/.git\* plugin.video.flix2kodi/copy2repo.sh plugin.video.flix2kodi/read_version.py plugin.video.flix2kodi/test\* plugin.video.flix2kodi/.git* plugin.video.flix2kodi/.idea\*
cd logi85.github.io
/usr/bin/python3 init.py
git add .
git commit -m "Version $VERSION"
