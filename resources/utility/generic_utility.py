from __future__ import unicode_literals

import HTMLParser
import json
import os
import sys
import urllib


test_settings = {}
test = False
try:
    import xbmc
    import xbmcaddon
    import xbmcvfs
except Exception:
    test = True



addon_id = 'plugin.video.flix2kodi'
addon_name = 'Flix2Kodi'
if test == False:
    addon_handle = xbmcaddon.Addon(addon_id)

# urls for netflix
main_url = 'https://www.netflix.com/'
kids_url = 'https://www.netflix.com/Kids'
api_url = 'https://www.netflix.com/api/shakti'
evaluator_url = '%s/pathEvaluator/%s?materialize=true&model=harris'
profile_switch_url = '%s/profiles/switch/%s?'
profile_url = 'http://api-global.netflix.com/desktop/account/profiles?version=2&withCredentials=true'
series_url = '%s/metadata/%s?movieid=%s&imageFormat=jpg'
activity_url = '%s/viewingactivity/%s?_retry=0&authURL=%s'

# post data information

movie_genre = '{"paths":[["genreList",{"from":0,"to":24},["id","menuName"]]],"authURL":"%s"}'
series_genre = '{"paths":[["genres",83,"subgenres",{"from":0,"to":20},"summary"]],"authURL":"%s"}'
video_playback_info = '{"paths": [["videos",[%s],["bookmarkPosition","runtime","summary"]]],"authURL":"%s"}'


def data_dir():
    return xbmc.translatePath('special://profile/addon_data/' + addon_id + '/')


def cache_dir():
    return xbmc.translatePath('special://profile/addon_data/' + addon_id + '/cache/')


def headers_file():
    return xbmc.translatePath('special://profile/addon_data/' + addon_id + '/headers')


def cookies_file():
    return xbmc.translatePath('special://profile/addon_data/' + addon_id + '/cookies')


def library_dir():
    return get_setting('library_path')


def movie_dir():
    return xbmc.translatePath(library_dir() + '/movies/')


def tv_dir():
    return xbmc.translatePath(library_dir() + '/tv/')


def addon_dir():
    return addon_handle.getAddonInfo('path')


def addon_icon():
    return addon_handle.getAddonInfo('icon')


def addon_fanart():
    if not test:
        return addon_handle.getAddonInfo('fanart')
    else:
        return None

def create_pathname(path, item):
    ret = os.path.join(path, item)
    return ret


def evaluator():
    return evaluator_url % (api_url, endpoints()['/pathEvaluator'])


def endpoints():
    return json.loads(get_setting('endpoints'))

def auth_url():
    return get_setting('authorization_url')

def profile_switch():
    return profile_switch_url % (api_url, endpoints()['/profiles/switch'])

def error(message):
    if test == False:
        log(message, xbmc.LOGERROR)
    else:
        log(message)

def debug(message):
    if test == False:
        if get_setting('debug') == 'true':
            log(message)
    else:
        log(message)
def log(message, loglevel = None):
    logmsg = ("[%s] %s" % (addon_id, message)).encode('utf-8')
    if test == False:
        if loglevel == None:
            loglevel = xbmc.LOGNOTICE
        xbmc.log(logmsg, level=loglevel)
    else:
        print logmsg

def notification(message):
    xbmc.executebuiltin(encode('Notification(%s: , %s, 5000, %s)' % (addon_name, message, addon_icon())))

def open_setting():
    return addon_handle.openSettings()


def get_setting(name):
    if not test:
        ret = addon_handle.getSetting(name)
    else:
        if name not in test_settings:
            return None
        else:
            ret = test_settings[name]
    return ret


def set_setting(name, value):
    if not test:
        addon_handle.setSetting(name, value)
    else:
        test_settings[name] = value


def get_string(string_id):
    return addon_handle.getLocalizedString(string_id)


def decode(string):
    return string.decode('utf-8')


def encode(unicode):
    return unicode.encode('utf-8') if unicode else ''.encode('utf-8')


def clean_filename(n, chars=None):
    if isinstance(n, str):
        return (''.join(c for c in unicode(n, 'utf-8') if c not in '/\\:?"*|<>')).strip(chars)
    elif isinstance(n, unicode):
        return (''.join(c for c in n if c not in '/\\:?"*|<>')).strip(chars)


def sh_escape(s):
    return s.replace("(","\\(").replace(")","\\)").replace(" ","\\ ").replace("&", "\\&")

def unescape(string):
    html_parser = HTMLParser.HTMLParser()
    return html_parser.unescape(string)


def prepare_folders():
    if not xbmcvfs.exists(data_dir()):
        xbmcvfs.mkdir(data_dir())
    if not xbmcvfs.exists(cache_dir()):
        xbmcvfs.mkdir(cache_dir())
    if not os.path.isdir(library_dir()):
        xbmcvfs.mkdir(library_dir())
    if not os.path.isdir(movie_dir()):
        xbmcvfs.mkdir(movie_dir())
    if not os.path.isdir(tv_dir()):
        xbmcvfs.mkdir(tv_dir())


def parameters_to_dictionary(parameters):
    parameter_dictionary = {}
    if parameters:
        parameter_pairs = parameters[1:].split('&')
        for parameter_pair in parameter_pairs:
            parameter_splits = parameter_pair.split('=')
            if (len(parameter_splits)) == 2:
                parameter_dictionary[parameter_splits[0]] = parameter_splits[1]
    return parameter_dictionary


def get_parameter(parameters, parameter):
    return urllib.unquote_plus(str(parameters.get(parameter, ''))).decode('utf-8')


def progress_window(window_handle, value, message):
    window_handle.update(value, '', message, '')
    if window_handle.iscanceled():
        return False
    else:
        return True


def keyboard():
    keyboard_handle = xbmc.Keyboard('', get_string(30111))
    keyboard_handle.doModal()
    if keyboard_handle.isConfirmed() and keyboard_handle.getText():
        search_string = urllib.quote_plus(keyboard_handle.getText())
    else:
        search_string = None
    return search_string

def windows():
    return os.name == 'nt'

def darwin():
    return  sys.platform == 'darwin'

def android():
    if not test:
        return xbmc.getCondVisibility('System.Platform.Android')
    else:
        return False

