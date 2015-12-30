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


def video(video_metadata, removable = False, viewing_activity = False):
#    utility.log(str(video_metadata))

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
    if viewing_activity == False and utility.get_setting('browse_tv_shows') == 'true' and (type == 'tvshow' or type == 'episode'):
        next_mode = 'list_seasons'

    entries = []
    cover_file, fanart_file = utility.cover_fanart(video_id)
    if xbmcvfs.exists(cover_file):
        thumb_url = cover_file
    u = sys.argv[0]
    u += '?url=' + urllib.quote_plus(video_id)
    u += '&mode=' + next_mode
    u += '&name=' + urllib.quote_plus(utility.encode(title))
    u += '&thumb=' + urllib.quote_plus(thumb_url)
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
        list_item.setProperty('fanart_image', utility.addon_fanart())
    if type == 'tvshow':
        if utility.get_setting('browse_tv_shows') == 'true':
            entries.append((utility.get_string(30151),
                            'Container.Update(plugin://%s/?mode=play_video_main&url=%s&thumb=%s)' % (
                                utility.addon_id, urllib.quote_plus(video_id), urllib.quote_plus(thumb_url))))
        else:
            entries.append((utility.get_string(30152),
                            'Container.Update(plugin://%s/?mode=list_seasons&url=%s&thumb=%s)' % (
                                utility.addon_id, urllib.quote_plus(video_id), urllib.quote_plus(thumb_url))))
    if type != 'episode':
        entries.append((utility.get_string(30153), 'RunPlugin(plugin://%s/?mode=play_trailer&url=%s&type=%s)' % (
            utility.addon_id, urllib.quote_plus(utility.encode(title)), type)))
        if removable:
            entries.append((utility.get_string(30154), 'RunPlugin(plugin://%s/?mode=remove_from_queue&url=%s)' % (
                utility.addon_id, urllib.quote_plus(video_id))))
        else:
            entries.append((utility.get_string(30155), 'RunPlugin(plugin://%s/?mode=add_to_queue&url=%s)' % (
                utility.addon_id, urllib.quote_plus(video_id))))
        entries.append((utility.get_string(30156),
                        'Container.Update(plugin://%s/?mode=list_videos&url=%s&type=movie)' % (
                            utility.addon_id, urllib.quote_plus(utility.main_url + 'WiMovie/' + video_id))))
        entries.append((utility.get_string(30157), 'Container.Update(plugin://%s/?mode=list_videos&url=%s&type=tv)' % (
            utility.addon_id, urllib.quote_plus(utility.main_url + 'WiMovie/' + video_id))))
    if type == 'tvshow':
        entries.append((utility.get_string(30150),
                        'RunPlugin(plugin://%s/?mode=add_series_to_library&url=&name=%s&series_id=%s)' % (
                            utility.addon_id, urllib.quote_plus(utility.encode(title.strip())), urllib.quote_plus(video_id))))
    elif type == 'movie':
        title_utf8 = title.strip() + ' (' + str(year) + ')'
        title = urllib.quote_plus(title_utf8.encode('utf-8'))
#        utility.log(title)
#        utility.log(urllib.unquote_plus(title).decode('utf-8'))
#        utility.log(str(isinstance(title, unicode)))
        entries.append((utility.get_string(30150),
                        'RunPlugin(plugin://%s/?mode=add_movie_to_library&url=%s&name=%s)' % (
                            utility.addon_id, urllib.quote_plus(video_id),
                            title)))
#    utility.log(str(entries))
    list_item.addContextMenuItems(entries)

    folder = True
    if next_mode == 'play_video_main':
        folder = False
#    utility.log(u)
    directory_item = xbmcplugin.addDirectoryItem(handle=plugin_handle, url=u, listitem=list_item, isFolder=folder)
    return directory_item


def add_next_item(name, page, url, video_type, mode, iconimage):
    u = sys.argv[0]
    u += '?url=' + urllib.quote_plus(url)
    u += '&mode=' + mode
    u += '&type=' + video_type
    u += '&page=' + str(page)
    u += '&name=' + urllib.quote_plus(utility.encode(name))
    liz=xbmcgui.ListItem(unicode(name), iconImage="DefaultFolder.png",thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name })
    ok=xbmcplugin.addDirectoryItem(handle=plugin_handle,url=u,listitem=liz,isFolder=True)
    return ok

def season(name, url, thumb, series_name, series_id):
    entries = []
    cover_file, fanart_file = utility.cover_fanart(series_id)
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
        list_item.setProperty('fanart_image', utility.addon_fanart())
    entries.append((utility.get_string(30150),
                    'RunPlugin(plugin://%s/?mode=add_series_to_library&url=%s&name=%s&series_id=%s)' % (
                        utility.addon_id, urllib.quote_plus(unicode(url)),
                        urllib.quote_plus(utility.encode(series_name.strip())),
                        series_id)))
    list_item.addContextMenuItems(entries)
    directory_item = xbmcplugin.addDirectoryItem(handle=plugin_handle, url=u, listitem=list_item, isFolder=True)
    return directory_item


def episode(episode):
    series_id, episode_id, name, description, episode_nr, season_nr, duration, thumb, playcount = episode

    cover_file, fanart_file = utility.cover_fanart(series_id)
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
        list_item.setProperty('fanart_image', utility.addon_fanart())
    directory_item = xbmcplugin.addDirectoryItem(handle=plugin_handle, url=u, listitem=list_item, isFolder=False)
    return directory_item
