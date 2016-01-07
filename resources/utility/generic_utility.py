from __future__ import unicode_literals

import HTMLParser
import os
import urllib
import json
import re
import sys

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
evaluator_url = '%s/pathEvaluator?materialize=true&model=harris'
profile_switch_url = '%s/profiles/switch?'
profile_url = 'http://api-global.netflix.com/desktop/account/profiles?version=2&withCredentials=true'
picture_url = 'https://image.tmdb.org/t/p/original'
series_url = '%s/metadata?movieid=%s&imageFormat=jpg'
tmdb_url = 'https://api.themoviedb.org/3/search/%s?api_key=%s&query=%s&language=de'
activity_url = '%s/viewingactivity?_retry=0&authURL=%s'

# post data information
genre = '{"paths":[["genres",%s,"su",{"from":%s,"to":%s},["summary","title"]]],"authURL":"%s"}'
list_paths = '{"paths":[["lists","%s",{"from":%s,"to":%s},["summary", "title"]]],"authURL":"%s"}'

movie_genre = '{"paths":[["genreList",{"from":0,"to":24},["id","menuName"]]],"authURL":"%s"}'
series_genre = '{"paths":[["genres",83,"subgenres",{"from":0,"to":20},"summary"]],"authURL":"%s"}'
video_info = '{"paths":[["videos",%s,["availability","bookmarkPosition","details","episodeCount","maturity",' \
             '"queue","releaseYear","requestId","runtime","seasonCount","summary","title","userRating","watched"]],' \
             '["videos",%s,"current",["summary","runtime","bookmarkPosition","creditsOffset","title"]],' \
             '["videos",%s,"seasonList","current",["showMemberType","summary"]],["videos",%s,' \
             '"boxarts",["_342x192","_665x375"],"jpg"]],"authURL":"%s"}'
add_list = '{"callPath":["lolomos","%s","addToList"],"params":["%s",2,["videos",%s],%s,null,null],"paths":[],' \
           '"pathSuffixes":[[["length","trackIds","context","displayName"]],[{"to":%s}],["watchedEvidence",' \
           '{"to":2}]],"authURL":"%s"}'
video_playback_info = '{"paths": [["videos",[%s],["bookmarkPosition","runtime","summary"]]],"authURL":"%s"}'

def data_dir():
    return xbmc.translatePath('special://profile/addon_data/' + addon_id + '/')


def cache_dir():
    return xbmc.translatePath('special://profile/addon_data/' + addon_id + '/cache/')


def cover_cache_dir():
    return xbmc.translatePath('special://profile/addon_data/' + addon_id + '/cache/cover/')


def fanart_cache_dir():
    return xbmc.translatePath('special://profile/addon_data/' + addon_id + '/cache/fanart/')


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
    return addon_handle.getAddonInfo('fanart')


def cover_fanart(name):
    filename = clean_filename(name) + '.jpg'
    cover_file = xbmc.translatePath(cover_cache_dir() + filename)
    fanart_file = xbmc.translatePath(fanart_cache_dir() + filename)
    return cover_file, fanart_file


def create_pathname(path, item):
    ret = os.path.join(path, item)
    return ret


def evaluator():
    return evaluator_url % get_setting('api_url')

def profile_switch():
    return profile_switch_url % get_setting('api_url')

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
    return addon_handle.getSetting(name)


def set_setting(name, value):
    addon_handle.setSetting(name, value)


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
    if not xbmcvfs.exists(cover_cache_dir()):
        xbmcvfs.mkdir(cover_cache_dir())
    if not xbmcvfs.exists(fanart_cache_dir()):
        xbmcvfs.mkdir(fanart_cache_dir())
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


def parse_falkorcache(response):
    match = re.compile('netflix.falkorCache = ({.*});</script><script>window.netflix', re.DOTALL | re.UNICODE).findall(
        response)
    content = match[0]
    jsondata = json.loads(content)
    return jsondata


def read_lists(falkor_cache):

    mylist_id = extract_mylist_id(falkor_cache)[1]

    lists = falkor_cache['lists']
    lists = filter_size(lists)
    rets = []
    videos=[]

    list_contains_mylist = False
    for list_key in lists:
        list = lists[list_key]
        list = filter_size(list)
        if 'displayName' in list:
            if list_key == mylist_id:
                list_contains_mylist = True
            display_name = unicode(list['displayName']['value'])
            ret = {'id': list_key, 'name': display_name}
            rets.append(ret)

    if not list_contains_mylist:
        ret = {'id': mylist_id, 'name': get_string(30104)}
        rets.append(ret)

    return rets


def filter_size(lolomos):
    for key in lolomos.keys():
        if key in ('$size', 'size'):
            del lolomos[key]
    return lolomos


def extract_mylist_id(falkor_cache):
    mylist_id = None
    try:
        assert 'lolomos' in falkor_cache
        lolomos = falkor_cache['lolomos']
        filter_size(lolomos)
        assert len(lolomos)==1
        root_list_id = lolomos.keys()[0]
        lists = filter_size(lolomos[root_list_id])
        assert 'mylist' in lists
        mylist_ref = lists['mylist']
        assert len(mylist_ref) == 3
        mylist_idx = mylist_ref[2]
        assert mylist_idx in lists
        mylist = lists[mylist_idx]
        assert len(mylist) == 2
        mylist_id = mylist[1]
    except Exception as ex:
        print('cannot find mylist_id')
        print repr(ex)
    return root_list_id, mylist_id