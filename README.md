# plugin.video.netflix
kodi addon

Python newer than 2.7.6 is necessary otherwise you get an EOF error during request of https urls.
Also, Chrome is needed.
For Linux, install xdotool, and make sure to run a desktop environment like lxdm. (Without fullscreen is not working).

Library:
If you want to add something to kodi-library, first add the right path to video-sources.
Under Linux this will be something like:
/home/[user]/.kodi/userdata/addon_data/plugin.video.netflix/library/movies/
/home/[user]/.kodi/userdata/addon_data/plugin.video.netflix/library/tv/
Under Windows like: C:\Users\myuser\AppData\Roaming\Kodi\...
After adding the path, you have to set the scrapper to movies or series.
Then you can add items to library in the plugin and they will appear in your library.
