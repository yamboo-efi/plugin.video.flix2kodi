from __future__ import unicode_literals

import sys
import urllib
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs

import utility

plugin_handle = int(sys.argv[1])


def directory(name, url, mode, thumb, type='', context_enable=True):
    entries = []
    name = utility.unescape(name)
    u = sys.argv[0]
    u += '?url=' + urllib.quote_plus(url)
    u += '&mode=' + mode
    u += '&thumb=' + urllib.quote_plus(thumb)
    u += '&type=' + type
    list_item = xbmcgui.ListItem(name)
    list_item.setArt({'icon': 'DefaultTVShows.png', 'thumb': thumb})
    list_item.setInfo(type='video', infoLabels={'title': name})
    if "/my-list" in url:
        entries.append(
            (utility.get_string(30150), 'RunPlugin(plugin://%s/?mode=add_my_list_to_library)' % utility.addon_id))
    list_item.setProperty('fanart_image', utility.addon_fanart())
    if context_enable:
        list_item.addContextMenuItems(entries)
    else:
        list_item.addContextMenuItems([], replaceItems=True)
    directory_item = xbmcplugin.addDirectoryItem(handle=plugin_handle, url=u, listitem=list_item, isFolder=True)
    return directory_item


def video(name, url, mode, thumb, video_type='', description='', duration='', year='', mpaa='', director='', genre='',
          rating=0.0, playcount=0, remove=False):
    entries = []
    filename = utility.clean_filename(url) + '.jpg'
    cover_file = xbmc.translatePath(utility.cover_cache_dir() + filename)
    fanart_file = xbmc.translatePath(utility.fanart_cache_dir() + filename)
    if xbmcvfs.exists(cover_file):
        thumb = cover_file
    u = sys.argv[0]
    u += '?url=' + urllib.quote_plus(url)
    u += '&mode=' + mode
    u += '&name=' + urllib.quote_plus(utility.encode(name))
    u += '&thumb=' + urllib.quote_plus(thumb)
    list_item = xbmcgui.ListItem(name)
    list_item.setArt({'icon': 'DefaultTVShows.png', 'thumb': thumb})
    list_item.setInfo(type='video',
                      infoLabels={'title': name, 'plot': description, 'duration': duration, 'year': int(year),
                                  'mpaa': mpaa, 'director': director, 'genre': genre, 'rating': rating,
                                  'playcount': playcount})
    if xbmcvfs.exists(fanart_file):
        list_item.setProperty('fanart_image', fanart_file)
    elif xbmcvfs.exists(cover_file):
        list_item.setProperty('fanart_image', cover_file)
    else:
        list_item.setProperty('fanart_image', utility.addon_fanart())
    if video_type == 'tvshow':
        if utility.get_setting('browse_tv_shows') == 'true':
            entries.append((utility.get_string(30151),
                            'Container.Update(plugin://%s/?mode=play_video_main&url=%s&thumb=%s)' % (
                                utility.addon_id, urllib.quote_plus(url), urllib.quote_plus(thumb))))
        else:
            entries.append((utility.get_string(30152),
                            'Container.Update(plugin://%s/?mode=list_seasons&url=%s&thumb=%s)' % (
                                utility.addon_id, urllib.quote_plus(url), urllib.quote_plus(thumb))))
    if video_type != 'episode':
        entries.append((utility.get_string(30153), 'RunPlugin(plugin://%s/?mode=play_trailer&url=%s&type=%s)' % (
            utility.addon_id, urllib.quote_plus(utility.encode(name)), video_type)))
        if remove:
            entries.append((utility.get_string(30154), 'RunPlugin(plugin://%s/?mode=remove_from_queue&url=%s)' % (
                utility.addon_id, urllib.quote_plus(url))))
        else:
            entries.append((utility.get_string(30155), 'RunPlugin(plugin://%s/?mode=add_to_queue&url=%s)' % (
                utility.addon_id, urllib.quote_plus(url))))
        entries.append((utility.get_string(30156),
                        'Container.Update(plugin://%s/?mode=list_videos&url=%s&type=movie)' % (
                            utility.addon_id, urllib.quote_plus(utility.main_url + '/WiMovie/' + url))))
        entries.append((utility.get_string(30157), 'Container.Update(plugin://%s/?mode=list_videos&url=%s&type=tv)' % (
            utility.addon_id, urllib.quote_plus(utility.main_url + '/WiMovie/' + url))))
    if video_type == 'tvshow':
        entries.append((utility.get_string(30150),
                        'RunPlugin(plugin://%s/?mode=add_series_to_library&url=&name=%s&series_id=%s)' % (
                            utility.addon_id, urllib.quote_plus(utility.encode(name.strip())), urllib.quote_plus(url))))
    elif video_type == 'movie':
        entries.append((utility.get_string(30150),
                        'RunPlugin(plugin://%s/?mode=add_movie_to_library&url=%s&name=%s)' % (
                            utility.addon_id, urllib.quote_plus(url),
                            urllib.quote_plus(utility.encode(name.strip())) + ' (' + unicode(year) + ')')))
    list_item.addContextMenuItems(entries)
    directory_item = xbmcplugin.addDirectoryItem(handle=plugin_handle, url=u, listitem=list_item, isFolder=True)
    return directory_item


def season(name, url, mode, thumb, series_name, series_id):
    entries = []
    filename = series_id + '.jpg'
    cover_file = xbmc.translatePath(utility.cover_cache_dir() + filename)
    fanart_file = xbmc.translatePath(utility.fanart_cache_dir() + filename)
    u = sys.argv[0]
    u += '?url=' + urllib.quote_plus(unicode(url))
    u += '&mode=' + mode
    u += '&series_id=' + urllib.quote_plus(series_id)
    list_item = xbmcgui.ListItem(name)
    list_item.setArt({'icon': 'DefaultTVShows.png', 'thumb': thumb})
    list_item.setInfo(type='video', infoLabels={'title': name})
    if xbmcvfs.exists(fanart_file):
        list_item.setProperty('fanart_image', fanart_file)
    elif xbmcvfs.exists(cover_file):
        list_item.setProperty('fanart_image', cover_file)
    else:
        list_item.setProperty('fanart_image', utility.addon_fanart())
    entries.append((utility.get_string(30150),
                    'RunPlugin(plugin://%s/?mode=add_series_to_library&url=%s&name=%s&series_id=%s)' % (
                        utility.addon_id, urllib.quote_plus(unicode(url)),
                        urllib.quote_plus(utility.encode(series_name.strip())),
                        series_id)))
    list_item.addContextMenuItems(entries)
    directory_item = xbmcplugin.addDirectoryItem(handle=plugin_handle, url=u, listitem=list_item, isFolder=True)
    return directory_item


def episode(name, url, mode, thumb, description='', duration='', season_nr='', episode_nr='', series_id='',
            playcount=0):
    filename = series_id + '.jpg'
    cover_file = xbmc.translatePath(utility.cover_cache_dir() + filename)
    fanart_file = xbmc.translatePath(utility.fanart_cache_dir() + filename)
    u = sys.argv[0]
    u += '?url=' + urllib.quote_plus(unicode(url))
    u += '&mode=' + mode
    u += '&series_id=' + urllib.quote_plus(series_id)
    list_item = xbmcgui.ListItem(name)
    list_item.setArt({'icon': 'DefaultTVShows.png', 'thumb': thumb})
    list_item.setInfo(type='video',
                      infoLabels={'title': name, 'plot': description, 'duration': duration, 'season': season_nr,
                                  'episode': episode_nr, 'playcount': playcount})
    if xbmcvfs.exists(fanart_file):
        list_item.setProperty('fanart_image', fanart_file)
    elif xbmcvfs.exists(cover_file):
        list_item.setProperty('fanart_image', cover_file)
    else:
        list_item.setProperty('fanart_image', utility.addon_fanart())
    directory_item = xbmcplugin.addDirectoryItem(handle=plugin_handle, url=u, listitem=list_item, isFolder=True)
    return directory_item
