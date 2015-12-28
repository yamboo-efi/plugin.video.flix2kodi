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
        proc = subprocess.Popen(['sh '''+addon_path+'/resources/findChromeWindow.sh'''], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        return out

    def onAction(self, action):
        ACTION_NAV_BACK = 92
        ACTION_PREVIOUS_MENU = 10
        ACTION_STOP = 13

        ACTION_SELECT_ITEM = 7
        ACTION_PLAYER_PLAY = 79
        ACTION_PLAYER_PLAYPAUSE = 229
        ACTION_PAUSE = 12

        ACTION_PLAYER_REWIND = 78
        ACTION_MOVE_LEFT = 1
        ACTION_REWIND = 17

        ACTION_PLAYER_FORWARD = 77
        ACTION_MOVE_RIGHT = 2
        ACTION_FORWARD = 16

        ACTION_MOVE_UP = 3
        ACTION_MOVE_DOWN = 4

        if action.getId() in(ACTION_NAV_BACK, ACTION_PREVIOUS_MENU, ACTION_STOP):
            control('close')
        elif action.getId() in(ACTION_SELECT_ITEM, ACTION_PLAYER_PLAY, ACTION_PLAYER_PLAYPAUSE, ACTION_PAUSE):
            control('pause')
        elif action.getId() in(ACTION_PLAYER_REWIND, ACTION_MOVE_LEFT, ACTION_REWIND):
            control('backward')
        elif action.getId() in(ACTION_PLAYER_FORWARD, ACTION_MOVE_RIGHT, ACTION_FORWARD):
            control('forward')
        elif action.getId() == ACTION_MOVE_UP:
            control('up')
        elif action.getId() == ACTION_MOVE_DOWN:
            control('down')
        else:
            utility.log('unknown action: '+str(action.getId()))

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
        info = subprocess.STARTUPINFO()
        info.dwFlags = subprocess.STARTF_USESTDHANDLES | subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = subprocess.SW_HIDE
        process = subprocess.Popen('cscript "'+utility.addon_dir()+'\\resources\\sendKey.vbs" '+key, startupinfo=info)
        process.wait()
#    os.system(

    def launch_browser_linux(self, url):
        launchScript = 'launchBrowser'
        if(utility.get_setting('chromelauncher')== 'true'):
            launchScript = 'launchChromeLauncher'
        os.system('sh '''+addon_path+'/resources/'+launchScript+'.sh'' ' + url)

    def launch_browser_windows(self, url):
        info = subprocess.STARTUPINFO()
        info.dwFlags = subprocess.STARTF_USESTDHANDLES | subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = subprocess.SW_HIDE

        launchScript = 'launchBrowser'
        if(utility.get_setting('chromelauncher')== 'true'):
            launchScript = 'launchChromeLauncher'

        process = subprocess.Popen('"'+addon_path+'\\resources\\'+launchScript+'.cmd" ' + url, startupinfo=info)
        process.wait()

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