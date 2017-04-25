from __future__ import unicode_literals

import os
import sys
import urllib
import xbmcgui
import xbmcplugin
import xbmcvfs

from resources import library
from resources import get
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
    fanart = generic_utility.addon_handle.getAddonInfo('fanart')

    if viewing_activity == False and generic_utility.get_setting('browse_tv_shows') == 'true' and (type == 'show'):
        next_mode = 'list_seasons'
    entries = []
    url = sys.argv[0]
    url += '?url=' + urllib.quote_plus(video_id)
    url += '&mode=' + next_mode
    url += '&name=' + urllib.quote_plus(generic_utility.encode(title))
    url += '&thumb=' + urllib.quote_plus(thumb_url)

    #get extended artwork if tmdb lookups are enabled
    if generic_utility.get_setting('use_tmdb') == 'true' and type in ["movie","show"]:
        extended_info = get.extended_artwork(title,year,type,video_metadata['video_id'])
    elif generic_utility.get_setting('use_tmdb') == 'true' and type == "episode":
        extended_info = get.extended_artwork(video_metadata['series_title'],year,type,video_metadata['series_id'])
    else: extended_info = {}

    defaulticon = "DefaultMovies.png"
    if type in ['season','show','episode']:
        defaulticon = "DefaultTVShows.png"

    #prepend watchdate to label for viewing_activity listings
    if viewing_activity:
        list_item = xbmcgui.ListItem("%s - %s" %(video_metadata.get("date_watched",""),title))
    else:
        list_item = xbmcgui.ListItem(title)

    artwork = {
        'icon': defaulticon,
        'thumb': extended_info.get("poster",thumb_url),
        'landscape': extended_info.get("landscape",thumb_url),
        'poster': extended_info.get("poster",thumb_url),
        'clearlogo': extended_info.get("clearlogo",thumb_url),
        'clearart': extended_info.get("clearart",thumb_url),
        'fanart': extended_info.get("fanart",thumb_url),
        'characterart': extended_info.get("characterart",thumb_url),
        'discart': extended_info.get("discart",thumb_url),
        'banner': extended_info.get("banner",thumb_url)
    }
    list_item.setArt(artwork)

    if type == 'show':
        add_context_menu_show(entries, removable, thumb_url, title, video_id)
        #get playcount from episodes

        #TODO: Commented to prevent request flood and consequent ban
        #playcount, total_episodes, watched_episodes, unwatched_episodes = get.series_playcounts(video_id)
        #list_item.setProperty("totalepisodes", str(total_episodes))
        #list_item.setProperty("watchedepisodes", str(watched_episodes))
        #list_item.setProperty("unwatchedepisodes", str(unwatched_episodes))
    else:
        add_context_menu_movie(entries, removable, title, type, video_id, year)

    list_item.setInfo(type='video', infoLabels= {
        'title': title,
        'duration': unicode(duration),
        'year': int(year),
        'mpaa': mpaa,
        'playcount': playcount,
        'cast': video_metadata.get("actors",[]),
        'castandrole': eval(extended_info.get("castandrole","[]")),
        'code': extended_info.get("imdb_id",""),
        'tagline': extended_info.get("tagline",""),
        'trailer': extended_info.get("trailer",""),
        'genre': extended_info.get("genre",genre),
        'studio': extended_info.get("studio",""),
        'plot': extended_info.get("plot",description),
        'plotoutline': description,
        'director': extended_info.get("director",director),
        'writer': extended_info.get("writer",""),
        'rating': float(extended_info.get("rating",rating)),
        'datewatched': video_metadata.get("date_watched","")
    })
    if type == "episode":
        list_item.setInfo(type='video', infoLabels= {
            'tvshowtitle': video_metadata.get("series_title",""),
            'episode': video_metadata.get("episode",None),
            'season': video_metadata.get("season",None)
        })

    list_item.setProperty('IsPlayable', 'true');

    list_item.addContextMenuItems(entries)
    folder = True
    if next_mode == 'play_video_main':
        folder = False

    #always set streaminfo to prevent kodi from probing the listitems
    if video_metadata.get("hd"):
        list_item.addStreamInfo("video", {"codec":"h264", "aspect":1.78, "width":1920, "height":1080, "duration":duration} )
        list_item.addStreamInfo("audio", {"codec":"pcm_s16le","channels":"2" })
    else:
        list_item.addStreamInfo("video", {"codec":"h264", "aspect":1.78, "width":720, "height":480, "duration":duration} )
        list_item.addStreamInfo("audio", {"codec":"pcm_s16le","channels":"2" })

    return url, list_item, folder


def add_context_menu_movie(entries, removable, title, type, video_id, year):
    entries.append((generic_utility.get_string(30156),
                    'Container.Update(plugin://%s/?mode=list_videos&url=%s&type=movie)' % (
                        generic_utility.addon_id, urllib.quote_plus(
                                generic_utility.main_url + 'WiMovie/' + video_id))))
    entries.append(
            (generic_utility.get_string(30157), 'Container.Update(plugin://%s/?mode=list_videos&url=%s&type=tv)' % (
                generic_utility.addon_id, urllib.quote_plus(generic_utility.main_url + 'WiMovie/' + video_id))))
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


def add_next_item(page, url, video_type, mode):
    name = generic_utility.get_string(30110)
    u = sys.argv[0]
    u += '?url=' + urllib.quote_plus(url)
    u += '&mode=' + mode
    u += '&type=' + video_type
    u += '&page=' + str(page)
    u += '&name=' + urllib.quote_plus(generic_utility.encode(name))
    liz=xbmcgui.ListItem(unicode(name), iconImage="DefaultFolder.png")
    liz.setInfo( type="Video", infoLabels={ "Title": name, "sorttitle": "zzzzzzz"})
    liz.setArt( { "thumb": generic_utility.addon_handle.getAddonInfo('icon'), "fanart":generic_utility.addon_handle.getAddonInfo('fanart') })
    liz.setProperty('IsPlayable', 'false');
    ok=xbmcplugin.addDirectoryItem(handle=plugin_handle,url=u,listitem=liz,isFolder=True)
    return ok

def season(item):
    entries = []
    u = sys.argv[0]
    u += '?url=' + urllib.quote_plus(unicode(item.get("season")))
    u += '&mode=list_episodes'
    u += '&series_id=' + urllib.quote_plus(item.get("series_id"))

    if generic_utility.get_setting('use_tmdb') == 'true':
        extended_info = get.extended_artwork(item.get("tvshowtitle"),item.get("tvshowyear"),"show",item.get("series_id"))
    else:
        extended_info = {}

    list_item = xbmcgui.ListItem(item.get("name"))
    artwork = {
        'icon': 'DefaultTVShows.png',
        'thumb': extended_info.get("poster", item.get("seriesthumb","")),
        'landscape': extended_info.get("landscape",item.get("seriesthumb","")),
        'poster': extended_info.get("poster",""),
        'clearlogo': extended_info.get("clearlogo",""),
        'clearart': extended_info.get("clearart",""),
        'fanart': extended_info.get("fanart",""),
        'characterart': extended_info.get("characterart",""),
        'discart': extended_info.get("discart",""),
        'banner': extended_info.get("banner","")
    }
    list_item.setArt(artwork)

    list_item.setInfo(type='video',infoLabels={
        'title': item.get("name",""),
        'year': item.get("year"),
        'playcount': item.get("playcount"),
        'tvshowtitle':item.get("tvshowtitle"),
        'castandrole': eval(extended_info.get("castandrole","[]")),
        'trailer': extended_info.get("trailer",""),
        'genre': extended_info.get("genre",""),
        'studio': extended_info.get("studio",""),
        'plot': extended_info.get("plot",item.get("description","")),
        'plotoutline': item.get("description",""),
        'director': extended_info.get("director",""),
        'writer': extended_info.get("writer",""),
        'rating': float(extended_info.get("rating","0")),
        })
    list_item.setProperty("totalepisodes", str(item.get("total_episodes","")))
    list_item.setProperty("watchedepisodes", str(item.get("watched_episodes","")))
    list_item.setProperty("unwatchedepisodes", str(item.get("unwatched_episodes","")))
    entries.append((generic_utility.get_string(30150),
                    'RunPlugin(plugin://%s/?mode=add_series_to_library&url=%s&name=%s&series_id=%s)' % (
                        generic_utility.addon_id, urllib.quote_plus(unicode(item.get("season"))),
                        urllib.quote_plus(generic_utility.encode(item.get("tvshowtitle").strip())),
                        item.get("series_id"))))
    list_item.addContextMenuItems(entries)
    directory_item = xbmcplugin.addDirectoryItem(handle=plugin_handle, url=u, listitem=list_item, isFolder=True)
    return directory_item


def episode(episode):
    name = episode.get("episode_title")
    u = sys.argv[0]
    u += '?url=' + urllib.quote_plus(unicode(episode.get("episode_id")))
    u += '&mode=play_video_main'
    u += '&series_id=' + urllib.quote_plus(episode.get("series_id"))

    if generic_utility.get_setting('use_tmdb') == 'true':
        extended_info = get.extended_artwork(episode.get("tvshowtitle"),episode.get("tvshowyear"),"show",episode.get("series_id"))
    else:
        extended_info = {}

    list_item = xbmcgui.ListItem(name)
    artwork = {
        'icon': 'DefaultTVShows.png',
        'thumb': episode.get("thumb"),
        'landscape': extended_info.get("landscape",episode.get("seriesthumb")),
        'poster': extended_info.get("poster",""),
        'clearlogo': extended_info.get("clearlogo",""),
        'clearart': extended_info.get("clearart",""),
        'fanart': extended_info.get("fanart",""),
        'characterart': extended_info.get("characterart",""),
        'discart': extended_info.get("discart",""),
        'banner': extended_info.get("banner","")
    }
    list_item.setArt(artwork)

    list_item.setInfo(type='video',infoLabels={
        'title': name,
        'plot': episode.get("description"),
        'rating': episode.get("rating"),
        'duration': episode.get("duration"),
        'season': episode.get("season"),
        'episode': episode.get("episode_nr"),
        'playcount': episode.get("playcount"),
        'tvshowtitle':episode.get("tvshowtitle")})

    if episode.get("hd"):
        list_item.addStreamInfo("video", {"codec":"h264", "aspect":1.78, "width":1920, "height":1080, "duration":episode.get("duration")} )
    list_item.addStreamInfo("audio", {"codec":"pcm_s16le","channels":"2" })
    directory_item = xbmcplugin.addDirectoryItem(handle=plugin_handle, url=u, listitem=list_item, isFolder=False)
    return directory_item
