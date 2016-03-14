from __future__ import unicode_literals

import os
import sys
import urllib
import xbmcgui
import xbmcplugin
import xbmcvfs

from resources import library
from resources.utility import generic_utility

plugin_handle = int(sys.argv[1])


def directory(name, url, mode, thumb, type='', context_enable=True, login_context = False):
    entries = []
    name = generic_utility.unescape(name)
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
            (generic_utility.get_string(30150), 'RunPlugin(plugin://%s/?mode=add_my_list_to_library)' % generic_utility.addon_id))
    list_item.setProperty('fanart_image', generic_utility.addon_fanart())
    if context_enable:
        if login_context == True:
            entries.append(('Relogin',
                            'RunPlugin(plugin://%s/?mode=relogin)' % (
                                generic_utility.addon_id)))

        list_item.addContextMenuItems(entries)
    else:
        list_item.addContextMenuItems([], replaceItems=True)
    directory_item = xbmcplugin.addDirectoryItem(handle=plugin_handle, url=u, listitem=list_item, isFolder=True)
    return directory_item

def item(name, mode, login_context = False, context_enable = True):
    entries = []
    name = generic_utility.unescape(name)
    u = sys.argv[0]
    u += '?mode=' + mode
#    generic_utility.log(u)

    list_item = xbmcgui.ListItem(name)
    if context_enable:
        if login_context == True:
            entries.append(('Relogin',
                            'RunPlugin(plugin://%s/?mode=relogin)' % (
                                generic_utility.addon_id)))

        list_item.addContextMenuItems(entries)
    else:
        list_item.addContextMenuItems([], replaceItems=True)
    directory_item = xbmcplugin.addDirectoryItem(handle=plugin_handle, url=u, listitem=list_item, isFolder=False)
    return directory_item


def videos(video_metadatas, removable = False, viewing_activity = False):
    items = []
    for video_metadata in video_metadatas:
        items.append(create_video_listitem(removable, video_metadata, viewing_activity))
    return xbmcplugin.addDirectoryItems(handle=plugin_handle, items=items, totalItems=len(items))


def create_video_listitem(removable, video_metadata, viewing_activity):
    title = video_metadata['title']
    video_id = video_metadata['video_id']
    thumb_url = video_metadata['thumb_url']
    type = video_metadata['type']
    description = video_metadata['description']
    duration = video_metadata['duration']
    year = video_metadata['year']
    mpaa = video_metadata['mpaa']
    director = video_metadata['director']
    genre = video_metadata['genre']
    rating = video_metadata['rating']
    playcount = video_metadata['playcount']
    next_mode = 'play_video_main'
    if viewing_activity == False and generic_utility.get_setting('browse_tv_shows') == 'true' and (type == 'show'):
        next_mode = 'list_seasons'
    entries = []
    cover_file, fanart_file = generic_utility.cover_fanart(video_id)
    if xbmcvfs.exists(cover_file):
        thumb_url = cover_file
    url = sys.argv[0]
    url += '?url=' + urllib.quote_plus(video_id)
    url += '&mode=' + next_mode
    url += '&name=' + urllib.quote_plus(generic_utility.encode(title))
    url += '&thumb=' + urllib.quote_plus(thumb_url)
    list_item = xbmcgui.ListItem(title)
    list_item.setArt({'icon': 'DefaultTVShows.png', 'thumb': thumb_url})
    list_item.setInfo(type='video',
                      infoLabels={'title': title, 'plot': description, 'duration': unicode(duration), 'year': int(year),
                                  'mpaa': mpaa, 'director': director, 'genre': genre, 'rating': rating,
                                  'playcount': playcount})
    list_item.setProperty('IsPlayable', 'true');
    if xbmcvfs.exists(fanart_file):
        list_item.setProperty('fanart_image', fanart_file)
    elif xbmcvfs.exists(cover_file):
        list_item.setProperty('fanart_image', cover_file)
    else:
        list_item.setProperty('fanart_image', thumb_url)
    if type == 'show':
        add_context_menu_show(entries, removable, thumb_url, title, video_id)
    else:
        add_context_menu_movie(entries, removable, title, type, video_id, year)
    list_item.addContextMenuItems(entries)
    folder = True
    if next_mode == 'play_video_main':
        folder = False
    #    utility.log(u)
    return url, list_item, folder


def add_context_menu_movie(entries, removable, title, type, video_id, year):
    entries.append((generic_utility.get_string(30156),
                    'Container.Update(plugin://%s/?mode=list_videos&url=%s&type=movie)' % (
                        generic_utility.addon_id, urllib.quote_plus(
                                generic_utility.main_url + 'WiMovie/' + video_id))))
    entries.append(
            (generic_utility.get_string(30157), 'Container.Update(plugin://%s/?mode=list_videos&url=%s&type=tv)' % (
                generic_utility.addon_id, urllib.quote_plus(generic_utility.main_url + 'WiMovie/' + video_id))))

    if generic_utility.get_setting('is_kid') == 'false':
        if removable:
            entries.append((generic_utility.get_string(30154), 'RunPlugin(plugin://%s/?mode=remove_from_queue&url=%s)' % (
                generic_utility.addon_id, urllib.quote_plus(video_id))))
        else:
            entries.append((generic_utility.get_string(30155), 'RunPlugin(plugin://%s/?mode=add_to_queue&url=%s)' % (
                generic_utility.addon_id, urllib.quote_plus(video_id))))

    title_utf8 = title.strip() + ' (' + str(year) + ')'
    title = urllib.quote_plus(title_utf8.encode('utf-8'))
    movie_dir = library.get_movie_dir(title_utf8)[0]
    if xbmcvfs.exists(movie_dir + os.sep) == False:
        entries.append((generic_utility.get_string(30150),
                        'RunPlugin(plugin://%s/?mode=add_movie_to_library&url=%s&name=%s)' % (
                            generic_utility.addon_id, urllib.quote_plus(video_id),
                            title)))
    else:
        entries.append((generic_utility.get_string(301501),
                        'RunPlugin(plugin://%s/?mode=remove_movie_from_library&url=&name=%s)' % (
                            generic_utility.addon_id, title)))


def add_context_menu_show(entries, removable, thumb_url, title, video_id):
    if generic_utility.get_setting('browse_tv_shows') == 'true':
        entries.append((generic_utility.get_string(30151),
                        'RunPlugin(plugin://%s/?mode=play_video_main&url=%s&thumb=%s)' % (
                            generic_utility.addon_id, urllib.quote_plus(video_id), urllib.quote_plus(thumb_url))))

    else:
        entries.append((generic_utility.get_string(30152),
                        'Container.Update(plugin://%s/?mode=list_seasons&url=%s&thumb=%s)' % (
                            generic_utility.addon_id, urllib.quote_plus(video_id), urllib.quote_plus(thumb_url))))

    if generic_utility.get_setting('is_kid') == 'false':
        if removable:
            entries.append((generic_utility.get_string(30154), 'RunPlugin(plugin://%s/?mode=remove_from_queue&url=%s)' % (
                generic_utility.addon_id, urllib.quote_plus(video_id))))
        else:
            entries.append((generic_utility.get_string(30155), 'RunPlugin(plugin://%s/?mode=add_to_queue&url=%s)' % (
                generic_utility.addon_id, urllib.quote_plus(video_id))))

    series_dir = library.get_series_dir(title.strip())
    #        generic_utility.log('series-dir: '+series_dir)
    if xbmcvfs.exists(series_dir + os.sep) == False:
        entries.append((generic_utility.get_string(30150),
                        'RunPlugin(plugin://%s/?mode=add_series_to_library&url=&name=%s&series_id=%s)' % (
                            generic_utility.addon_id, urllib.quote_plus(generic_utility.encode(title.strip())),
                            urllib.quote_plus(video_id))))
    else:
        entries.append((generic_utility.get_string(301501),
                        'RunPlugin(plugin://%s/?mode=remove_series_from_library&url=&name=%s)' % (
                            generic_utility.addon_id, urllib.quote_plus(generic_utility.encode(title.strip())))))


def add_next_item(name, page, url, video_type, mode, iconimage):
    u = sys.argv[0]
    u += '?url=' + urllib.quote_plus(url)
    u += '&mode=' + mode
    u += '&type=' + video_type
    u += '&page=' + str(page)
    u += '&name=' + urllib.quote_plus(generic_utility.encode(name))
    liz=xbmcgui.ListItem(unicode(name), iconImage="DefaultFolder.png",thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Year":9999 })
    ok=xbmcplugin.addDirectoryItem(handle=plugin_handle,url=u,listitem=liz,isFolder=True)
    return ok

def season(name, url, thumb, series_name, series_id):
    entries = []
    cover_file, fanart_file = generic_utility.cover_fanart(series_id)
    u = sys.argv[0]
    u += '?url=' + urllib.quote_plus(unicode(url))
    u += '&mode=list_episodes'
    u += '&series_id=' + urllib.quote_plus(series_id)
    list_item = xbmcgui.ListItem(name)
    list_item.setArt({'icon': 'DefaultTVShows.png', 'thumb': thumb})
    list_item.setInfo(type='video', infoLabels={'title': name})
    if xbmcvfs.exists(fanart_file):
        list_item.setProperty('fanart_image', fanart_file)
    elif xbmcvfs.exists(cover_file):
        list_item.setProperty('fanart_image', cover_file)
    else:
        list_item.setProperty('fanart_image', generic_utility.addon_fanart())
    entries.append((generic_utility.get_string(30150),
                    'RunPlugin(plugin://%s/?mode=add_series_to_library&url=%s&name=%s&series_id=%s)' % (
                        generic_utility.addon_id, urllib.quote_plus(unicode(url)),
                        urllib.quote_plus(generic_utility.encode(series_name.strip())),
                        series_id)))
    list_item.addContextMenuItems(entries)
    directory_item = xbmcplugin.addDirectoryItem(handle=plugin_handle, url=u, listitem=list_item, isFolder=True)
    return directory_item


def episode(episode):
    series_id, episode_id, name, description, episode_nr, season_nr, duration, thumb, playcount = episode

    cover_file, fanart_file = generic_utility.cover_fanart(series_id)
    u = sys.argv[0]
    u += '?url=' + urllib.quote_plus(unicode(episode_id))
    u += '&mode=play_video_main'
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
        list_item.setProperty('fanart_image', generic_utility.addon_fanart())
    directory_item = xbmcplugin.addDirectoryItem(handle=plugin_handle, url=u, listitem=list_item, isFolder=False)
    return directory_item
