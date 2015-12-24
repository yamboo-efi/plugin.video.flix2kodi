from __future__ import unicode_literals

import json
import subprocess
from thread import start_new_thread

import time
import xbmc, xbmcgui, xbmcaddon, xbmcplugin

import get
import utility
import os
import sys

plugin_handle = int(sys.argv[1])

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
    xbmc.Player().stop()
    player = LogiPlayer()
    player.play( url )
    listitem = xbmcgui.ListItem(path=utility.addon_dir()+'/resources/fakeVid.mp4')
    xbmcplugin.setResolvedUrl(plugin_handle, True, listitem)
    xbmc.PlayList(xbmc.PLAYLIST_VIDEO).clear()
    player.doModal()
    return None


chrome_handle = None
class LogiPlayer(xbmcgui.Window):
    screensaver = None
    display_off = None
    addon_path = None
    control = None
    launch_browser = None

    def play ( self, url):
        start_new_thread(self.playInternal, (url,))
        start_new_thread(self.after_chrome_launched, ())

    def playInternal (self, url):
        xbmc.audioSuspend()
        self.disable_screensaver()
        launch_browser('https://www.netflix.com/watch/%s' % url)
        self.enable_screensaver()
        xbmc.audioResume()
        self.close()

    def disable_screensaver(self):
        global screensaver_mode, display_off
        ret = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 0, "method": "Settings.getSettingValue", "params": {"setting":"screensaver.mode" } }')
        jsn = json.loads(ret)
        screensaver_mode = jsn['result']['value']

        ret = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 0, "method": "Settings.getSettingValue", "params": {"setting":"powermanagement.displaysoff" } }')
        jsn = json.loads(ret)
        display_off = jsn['result']['value']

        xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 0, "method": "Settings.SetSettingValue", "params": {"setting": "screensaver.mode", "value": "" } }')
        xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 0, "method": "Settings.SetSettingValue", "params": {"setting": "powermanagement.displaysoff", "value": 0 } }')

    def enable_screensaver(self):
        global screensaver_mode, display_off
        xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 0, "method": "Settings.SetSettingValue", "params": {"setting":"screensaver.mode", "value": "'+screensaver_mode+'" } }')
        xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 0, "method": "Settings.SetSettingValue", "params": {"setting":"powermanagement.displaysoff", "value": '+str(display_off)+' } }')
    def after_chrome_launched(self):
        if utility.windows() == False:
            self.get_chrome_window_handle_linux()

    def get_chrome_window_handle_linux(self):
        global chrome_handle
        tries = 0
        handle = self.find_chrome_window_handle_linux()
        while (handle == '' and tries < 30):
            time.sleep(1)
            handle = self.find_chrome_window_handle_linux()
            tries+=1

        if handle == '':
            utility.log('cannot find chrome after 30 seconds!', xbmc.LOGERROR)
            self.close()
        chrome_handle = handle.strip()

    def find_chrome_window_handle_linux(self):
        proc = subprocess.Popen(['sh '+addon_path+'/resources/findChromeWindow.sh'], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        return out


    def onAction(self, action):
#        utility.log(str(action.getId()))
        if action.getId() in(92,10,13):
            control('close')
        if action.getId() == (7, 79):
            control('pause')
        if action.getId() == 1:
            control('backward')
        if action.getId() == 2:
            control('forward')
        if action.getId() == 3:
            control('up')
        if action.getId() == 4:
            control('down')

    def control_linux(self, key):
        if chrome_handle != None:
            cmd = None
            if key=='close':
                cmd = 'alt+F4'
            if key=='pause':
                cmd = 'space'
            if key=='backward':
                cmd = 'Left space'
            if key=='down':
                cmd = 'Left Left space'
            if key=='forward':
                cmd = 'Right space'
            if key=='up':
                cmd = 'Right Right space'
            os.system('/usr/bin/xdotool windowactivate --sync '+chrome_handle+' key '+cmd)


    def control_windows(self, key):
        os.system('cscript '+utility.addon_dir()+'\\resources\\sendKey.vbs '+key)

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