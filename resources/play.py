from __future__ import unicode_literals

import json
import os
import subprocess
import sys
import time
import traceback

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from thread import start_new_thread

import get
from resources.utility import generic_utility

plugin_handle = int(sys.argv[1])

BROWSER_CHROME='1'
BROWSER_CHROME_LAUNCHER = '2'
BROWSER_INTERNET_EXPLORER = '3'
BROWSER_EDGE = '4'
BROWSER_SAFARI = '5'

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
            generic_utility.notification(generic_utility.get_string(30305))
    else:
        generic_utility.notification(generic_utility.get_string(30305))
        pass


def video(url):
    xbmc.Player().stop()
    player = LogiPlayer()
    if player.has_valid_browser():
        player.play( url )
    listitem = xbmcgui.ListItem(path=generic_utility.addon_dir() + '/resources/fakeVid.mp4')
    xbmcplugin.setResolvedUrl(plugin_handle, True, listitem)
    xbmc.PlayList(xbmc.PLAYLIST_VIDEO).clear()
    if player.has_valid_browser():
        player.doModal()
    return None


class LogiPlayer(xbmcgui.Window):
    valid_browser = False
    browser = None
    screensaver = None
    display_off = None
    screensaver_mode = None
    addon_path = None

    def has_valid_browser(self):
        return self.valid_browser

    def play ( self, url):
        start_new_thread(self.playInternal, (url,))
        start_new_thread(self.after_chrome_launched, ())

    def playInternal (self, url):
        xbmc.audioSuspend()
        self.disable_screensaver()

        try:
            self.launch_browser('https://www.netflix.com/watch/%s' % url)
        except:
            generic_utility.log(traceback.format_exc(), xbmc.LOGERROR)
            generic_utility.notification('Error launching browser. See logfile')

        self.enable_screensaver()
        xbmc.audioResume()
        self.close()

    def disable_screensaver(self):
        ret = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 0, "method": "Settings.getSettingValue", "params": {"setting":"screensaver.mode" } }')
        jsn = json.loads(ret)
        self.screensaver_mode = jsn['result']['value']

        ret = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 0, "method": "Settings.getSettingValue", "params": {"setting":"powermanagement.displaysoff" } }')
        jsn = json.loads(ret)
        self.display_off = jsn['result']['value']

        xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 0, "method": "Settings.SetSettingValue", "params": {"setting": "screensaver.mode", "value": "" } }')
        xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 0, "method": "Settings.SetSettingValue", "params": {"setting": "powermanagement.displaysoff", "value": 0 } }')

    def enable_screensaver(self):
        xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 0, "method": "Settings.SetSettingValue", "params": {"setting":"screensaver.mode", "value": "'+self.screensaver_mode+'" } }')
        xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 0, "method": "Settings.SetSettingValue", "params": {"setting":"powermanagement.displaysoff", "value": '+str(self.display_off)+' } }')
    def after_chrome_launched(self):
        pass
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
            self.control('close')
        elif action.getId() in(ACTION_SELECT_ITEM, ACTION_PLAYER_PLAY, ACTION_PLAYER_PLAYPAUSE, ACTION_PAUSE):
            self.control('pause')
        elif action.getId() in(ACTION_PLAYER_REWIND, ACTION_MOVE_LEFT, ACTION_REWIND):
            self.control('backward')
        elif action.getId() in(ACTION_PLAYER_FORWARD, ACTION_MOVE_RIGHT, ACTION_FORWARD):
            self.control('forward')
        elif action.getId() == ACTION_MOVE_UP:
            self.control('up')
        elif action.getId() == ACTION_MOVE_DOWN:
            self.control('down')
        else:
            generic_utility.log('unknown action: ' + str(action.getId()))

    def control(self, key):
        info = None
        if generic_utility.windows():
            info = subprocess.STARTUPINFO()
            info.dwFlags = subprocess.STARTF_USESTDHANDLES | subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = subprocess.SW_HIDE
        script = self.get_launch_script('keysender')
#        generic_utility.log('launching keysender: '+script+' with key: '+key)
        if script:
            process = subprocess.Popen(script + ' ' +key, startupinfo=info, shell=True)
            process.wait()

    def launch_browser(self, url):
        info = None
        if generic_utility.windows():
            info = subprocess.STARTUPINFO()
            info.dwFlags = subprocess.STARTF_USESTDHANDLES | subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = subprocess.SW_HIDE

        script = self.get_launch_script('launcher')

        if script:
            generic_utility.debug('launching: '+script)

            process = subprocess.Popen(script + ' ' +url, startupinfo=info, shell=True)
            process.wait()
            generic_utility.debug('browser terminated')

    def get_launch_script(self, type):
        path = addon_path + '/resources/scripts/'+type+'/'
        browser_name = None
        double_quotes=''
        bash = ''
        if generic_utility.windows():
            path += 'windows/'
            ending = '.cmd'
            double_quotes = '"'
        elif generic_utility.darwin():
            path += 'darwin/'
            ending = '.sh'
            bash = 'sh '
        else:
            path += 'linux/'
            ending = '.sh'
            bash = 'sh '
        browser_name = self.get_browser_scriptname(browser_name)

        script = path+browser_name+ending
        custom_script = path+browser_name+"_custom"+ending
		
        if generic_utility.windows():
            script = script.replace('/','\\')
            custom_script = custom_script.replace('/','\\')
        
        if os.path.isfile(custom_script):
            script = custom_script
        elif not os.path.isfile(script):
            generic_utility.log('Script: '+script+' not found!')
            script = ''
        return bash + double_quotes+script+double_quotes

    def get_browser_scriptname(self, browser_name):
        if self.browser == BROWSER_CHROME:
            browser_name = 'chrome'
        elif self.browser == BROWSER_CHROME_LAUNCHER:
            browser_name = 'chromelauncher'
        elif self.browser == BROWSER_INTERNET_EXPLORER:
            browser_name = 'iexplore'
        elif self.browser == BROWSER_EDGE:
            browser_name = 'edge'
        elif self.browser == BROWSER_SAFARI:
            browser_name = 'safari'
        return browser_name

    def read_browser(self):
        self.browser = generic_utility.get_setting('browser')
        if self.browser not in(BROWSER_CHROME, BROWSER_CHROME_LAUNCHER, BROWSER_EDGE, BROWSER_INTERNET_EXPLORER, BROWSER_SAFARI):
            generic_utility.notification(generic_utility.get_string(50001))
            xbmc.sleep(2000)
            self.valid_browser = False
            generic_utility.open_setting()
        self.valid_browser = True

    def __init__(self):
        global addon_path
        self.read_browser()

        self.strActionInfo = xbmcgui.ControlLabel(180, 60, 1200, 400, '', 'font14', '0xFFBBBBFF')
        self.addControl(self.strActionInfo)
        self.strActionInfo.setLabel('Push BACK to go back. If your browser not launches, something went wrong.')

        addon_path = xbmcaddon.Addon().getAddonInfo("path")
