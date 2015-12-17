from __future__ import unicode_literals
from thread import start_new_thread
import xbmc, xbmcgui, xbmcaddon, xbmcplugin

import get
import utility
import os
import sys

def trailer(title, video_type):
    trailers = []
    content = get.trailer(video_type, title)
    if content:
        for match in content['results']:
            if match['site'] == 'YouTube':
                if match['iso_639_1']:
                    name = match['name'] + ' (' + match['iso_639_1'] + ')'
                else:
                    name = match['name']
                match = {'name': name, 'key': match['key']}
                trailers.append(match)
        if len(trailers) > 0:
            dialog = xbmcgui.Dialog()
            nr = dialog.select('Trailer', [match['name'] for match in trailers])
            if nr >= 0:
                selected_trailer = trailers[nr]
                match = 'PlayMedia(plugin://plugin.video.youtube/play/?video_id=%s)' % selected_trailer['key']
                xbmc.executebuiltin(match)
        else:
            utility.notification(utility.get_string(30305))
    else:
        utility.notification(utility.get_string(30305))
        pass


def video(url):
    player = LogiPlayer()
    player.play( url )
    return None


class LogiPlayer(xbmcgui.Window):
    addon_path = None
    control = None
    launch_browser = None
    def play ( self, url):
        start_new_thread(self.playInternal, (url,))
        self.doModal()

    def playInternal (self, url):
        xbmc.executebuiltin("PlayerControl(Stop)")
        xbmc.audioSuspend()
        launch_browser('https://www.netflix.com/watch/%s' % url)
        xbmc.audioResume()
        self.close()

    def onAction(self, action):
        xbmc.log('Action: ' + `action.getId()`, level=xbmc.LOGERROR)
        if action.getId() == 92:
            control('close')
            self.close()
        if action.getId() == 7:
            control('pause')
        if action.getId() == 1:
            control('backward')
        if action.getId() == 2:
            control('forward')

    def control_linux(self, key):
        cmd = None
        if key=='close':
            cmd = 'alt+F4'
        if key=='pause':
            cmd = 'space'
        if key=='backward':
            cmd = 'Left Left space'
        if key=='forward':
            cmd = 'Right Right space'
        os.system('/usr/bin/xdotool key '+cmd)


    def control_windows(self, key):
        cmd = None
        if key=='close':
            cmd = 'alt+F4'
        if key=='pause':
            cmd = 'space'
        if key=='backward':
            cmd = 'Left Left space'
        if key=='forward':
            cmd = 'Right Right space'
#        os.system('/usr/bin/xdotool key '+cmd)

    def launch_browser_linux(self, url):
        os.system('sh '+addon_path+'/resources/launchBrowser.sh ' + url)

    def launch_browser_windows(self, url):
        os.system(addon_path+'/resources/launchBrowser.cmd ' + url)

    def __init__(self):
        global addon_path, launch_browser, control
        self.strActionInfo = xbmcgui.ControlLabel(180, 60, 1200, 400, '', 'font14', '0xFFBBBBFF')
        self.addControl(self.strActionInfo)
        self.strActionInfo.setLabel('Push BACK to go back. If your browser not launches, something went wrong.')

        addon_path = xbmcaddon.Addon().getAddonInfo("path")

        if utility.windows():
            control = self.control_windows
            launch_browser = self.launch_browser_windows
        else:
            control = self.control_linux
            launch_browser = self.launch_browser_linux