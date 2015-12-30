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

    if xbmcvfs.exists(utility.headers_file()):
        xbmcvfs.delete(utility.headers_file())
        utility.log('Header file deleted.')
        utility.notification(30302)
