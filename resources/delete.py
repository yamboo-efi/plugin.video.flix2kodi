from __future__ import unicode_literals

import xbmcgui
import xbmcvfs

import utility
from resources import connect


def addon():
    dialog = xbmcgui.Dialog()
    if dialog.yesno(utility.addon_name + ':', utility.get_string(30307)):
        try:
            xbmcvfs.rmdir(utility.data_dir(), force=True)
            utility.log('Addon userdata folder deleted.')
            utility.notification(utility.get_string(30308))
        except Exception:
            pass


def cache():
    try:
        xbmcvfs.rmdir(utility.cache_dir(), force=True)
        utility.log('Cache folder deleted.')
        utility.notification(utility.get_string(30309))
    except Exception:
        pass


def cookies():
    if xbmcvfs.exists(utility.cookie_file()):
        xbmcvfs.delete(utility.cookie_file())
        utility.log('Cookie file deleted.')
        utility.notification(30301)

    for i in range(0, connect.MAX_SESSIONS):
        if xbmcvfs.exists(utility.session_file(i)):
            xbmcvfs.delete(utility.session_file(i))
            utility.log('Session file '+str(i)+' deleted.')
            utility.notification(30302)
