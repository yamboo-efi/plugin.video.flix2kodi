from __future__ import unicode_literals

import xbmcgui
import xbmcvfs

from resources.utility import generic_utility


def addon():
    dialog = xbmcgui.Dialog()
    if dialog.yesno(generic_utility.addon_name + ':', generic_utility.get_string(30307)):
        try:
            xbmcvfs.rmdir(generic_utility.data_dir(), force=True)
            generic_utility.log('Addon userdata folder deleted.')
            generic_utility.notification(generic_utility.get_string(30308))
        except Exception:
            pass


def cache():
    try:
        xbmcvfs.rmdir(generic_utility.cache_dir(), force=True)
        generic_utility.log('Cache folder deleted.')
        generic_utility.notification(generic_utility.get_string(30309))
    except Exception:
        pass


def cookies():
    if xbmcvfs.exists(generic_utility.cookies_file()):
        xbmcvfs.delete(generic_utility.cookies_file())
        generic_utility.notification(generic_utility.get_string(30301))

    if xbmcvfs.exists(generic_utility.headers_file()):
        xbmcvfs.delete(generic_utility.headers_file())
        generic_utility.notification(generic_utility.get_string(30302))
