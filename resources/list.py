from __future__ import unicode_literals

import requests
import threading

import thread
from requests.packages.urllib3.exceptions import HTTPError
from traceback import format_exc

import json
import re
import sys
import urllib
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs
import time
import traceback

import add
import connect
import delete
import get
import login
import profiles
import utility

plugin_handle = int(sys.argv[1])


def videos(url, video_type, offset, run_as_widget=False):
    if '' == offset:
        page = 0
    else:
        page = int(offset)

    post_data = ''
    i = 1
    loading_progress = None
    if not run_as_widget:
        loading_progress = xbmcgui.DialogProgress()
        loading_progress.create('Netflix', utility.get_string(30205) + '...')
        utility.progress_window(loading_progress, 0, '...')
    xbmcplugin.setContent(plugin_handle, 'movies')
    if not xbmcvfs.exists(utility.session_file()):
        login.login()

    target_url = utility.evaluator()
    if 'recently-added' in url:
        post_data = utility.recently_added % utility.get_setting('authorization_url')
    elif 'genre' in url:
        off_from = page * 6
        off_to = off_from + 4
#        utility.log('from:' + str(off_from)+' to: '+str(off_to))
        post_data = utility.genre % (url.split('?')[1], off_from,off_to, utility.get_setting('authorization_url'))
    elif 'my-list' in url:
        post_data = None
        target_url = utility.mylist_url

    response = connect.load_netflix_site(target_url, post=post_data)
#    utility.log(response)

    matches = []
    if 'my-list' in url:
        match = re.compile('netflix.falkorCache = ({.*});</script><script>window.netflix', re.DOTALL).findall(response)
        content = utility.decode(match[0])
        jsondata = json.loads(content)
        if 'videos' in jsondata:
            videos = jsondata['videos']
            for video in videos:
                if not video in ('$size', 'size'):
                    matches.append(video)
    else:
        content = utility.decode(response)
        jsondata = json.loads(content)
#        utility.log(str(jsondata))
        if 'videos' in jsondata['value']:
            matches = jsondata['value']['videos']

    lock = thread.allocate_lock()

    max_threads = 4
    threads = [None] * max_threads
    rets = [None] * max_threads
    video_add_args = []
    size = 0

    i = 0
    for video_id in matches:
        if(i==max_threads):
#            utility.log('max reached, waiting for join')
            for i in range(len(threads)):
                threads[i].join()
                video_add_args.append(rets[i])
                threads[i] = None
                rets[i] = None
#            utility.log('all joined')
            i = 0

#        utility.log(video_id)
        threads[i] = threading.Thread(target = procVideo, args = (video_id, video_type, url, lock, rets, i))
        threads[i].start()
#        utility.log('thread '+str(i)+' started')
        size+=1
        if not run_as_widget:
            utility.progress_window(loading_progress, size * 100 / len(matches), 'processing...')

        i+=1

    for i in range(len(threads)):
        if threads[i] != None:
            threads[i].join()
            video_add_args.append(rets[i])
            threads[i] = None
            rets[i] = None
#    utility.log('all joined')

    for video_add_arg in video_add_args:
        if(video_add_arg != None):
            video_add(video_add_arg)

    if 'genre' in url and len(video_add_args) > 0:
        add.add_next_item('Next', page + 1, url, video_type, 'list_videos', '')

    if utility.get_setting('force_view') == 'true' and not run_as_widget:
        xbmc.executebuiltin('Container.SetViewMode(' + utility.get_setting('view_id_videos') + ')')
    xbmcplugin.endOfDirectory(plugin_handle)



def procVideo(video_id, video_type, url, lock, rets, i):
#    utility.log('loading '+unicode(video_id))

    ret = None
    success = False
    while (success == False):
        try:
            ret = video(unicode(video_id), '', '', False, False, video_type, url, lock)
            success = True
        except requests.exceptions.HTTPError, e:
            if e.response.status_code == 429:
                time.sleep(2)
            else:
                utility.log('error loading video ' +unicode(video_id)+'\n'+ traceback.format_exc(), xbmc.LOGERROR)
                break
        except Exception as e:
            utility.log('error loading video ' +unicode(video_id)+'\n'+ traceback.format_exc(), xbmc.LOGERROR)
            break
#    utility.log('finished '+video_id)
    rets[i] = ret

def video(video_id, title, thumb_url, is_episode, hide_movies, video_type, url, lock = None):
    added = False
    director = ''
    genre = ''
    playcount = 0
    video_details = get.video_info(video_id, lock)
    match = json.loads(video_details)['value']['videos'][video_id]
#    utility.log(str(match))
    if not title:
        title = match['title']
    year = match['releaseYear']
    if not thumb_url:
        try:
            thumb_url = match['boxarts']['_665x375']['jpg']['url']
        except Exception:
            try:
                thumb_url = match['boxarts']['_342x192']['jpg']['url']
            except Exception:
                thumb_url = utility.addon_fanart()
    mpaa = match['maturity']['rating']['value']
    duration = match['runtime']
    offset = match['bookmarkPosition']
    try:
        if (duration > 0 and float(offset) / float(duration)) >= 0.9:
            playcount = 1
    except Exception:
        pass
    type = match['summary']['type']
    if type == 'movie':
        video_type_temp = type
    else:
        video_type_temp = 'tv'
        if is_episode:
            type = 'episode'
        else:
            type = 'tvshow'
            duration = ''
    if utility.get_setting('use_tmdb') == 'true':
        year_temp = year
        title_temp = title
        if ' - ' in title_temp:
            title_temp = title_temp[title_temp.index(' - '):]
        filename = video_id + '.jpg'
        filename_none = video_id + '.none'
        cover_file = xbmc.translatePath(utility.cover_cache_dir() + filename)
        cover_file_none = xbmc.translatePath(utility.cover_cache_dir() + filename_none)
        if not (xbmcvfs.exists(cover_file) or xbmcvfs.exists(cover_file_none)):
            utility.log('Downloading cover art. type: %s, video_id: %s, title: %s, year: %s' % (video_type_temp,
                                                                                                video_id, title_temp,
                                                                                                year_temp), xbmc.LOGDEBUG)
            get.cover(video_type_temp, video_id, title_temp, year_temp)
    description = match['details']['synopsis']
    try:
        director = match['details']['directors'][0]['name']
    except Exception:
        pass
    try:
        genre = match['details']['genres'][0]['name']
    except Exception:
        pass
    xbmc.log('match: '+str(match))
    rating = match['userRating']['average']
    next_mode = 'play_video_main'
    if utility.get_setting('browse_tv_shows') == 'true' and type == 'tvshow':
        next_mode = 'list_seasons'

    video_add_args = None
    if '/my-list' in url and video_type_temp == video_type:
        video_add_args = [title, video_id, next_mode, thumb_url, type, description, duration, year, mpaa,
                          director, genre, rating, playcount, True]
    elif type == 'movie' and hide_movies:
        pass
    elif video_type_temp == video_type or video_type == 'both':
        video_add_args = [title, video_id, next_mode, thumb_url, type, description, duration, year, mpaa,
                          director, genre, rating, playcount, False]

#    utility.log(str(video_add_args))
    return video_add_args

def video_add(args):
    title, video_id, next_mode, thumb_url, type, description, duration, year, mpaa, director, genre, rating, playcount, remove = args
    add.video(title, video_id, next_mode, thumb_url, type, description, duration, year, mpaa,
                  director, genre, rating, playcount, remove=remove)



def genres(video_type):
    post_data = ''
    match = []
    xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_LABEL)
    if not xbmcvfs.exists(utility.session_file()):
        login.login()
    if video_type == 'tv':
        post_data = utility.series_genre % utility.get_setting('authorization_url')
    elif video_type == 'movie':
        post_data = utility.movie_genre % utility.get_setting('authorization_url')
    else:
        pass
    content = utility.decode(connect.load_netflix_site(utility.evaluator(), post=post_data))
    matches = json.loads(content)['value']['genres']
    for item in matches:
        try:
            match.append((unicode(matches[item]['id']), matches[item]['menuName']))
        except Exception:
            try:
                match.append((unicode(matches[item]['summary']['id']), matches[item]['summary']['menuName']))
            except Exception:
                pass
    for genre_id, title in match:
        if video_type == 'tv':
            add.directory(title, 'genre?' + genre_id, 'list_videos', '', video_type)
        elif not genre_id == '83' and video_type == 'movie':
            add.directory(title, 'genre?' + genre_id, 'list_videos', '', video_type)
    xbmcplugin.endOfDirectory(plugin_handle)


def view_activity(video_type, run_as_widget=False):
    count = 0
    loading_progress = None
    if not run_as_widget:
        loading_progress = xbmcgui.DialogProgress()
        loading_progress.create('Netflix', utility.get_string(30205) + '...')
        utility.progress_window(loading_progress, 0, '...')
    xbmcplugin.setContent(plugin_handle, 'movies')
    if not xbmcvfs.exists(utility.session_file()):
        login.login()
    content = utility.decode(connect.load_netflix_site(utility.activity_url % (utility.get_setting('api_url'),
                                                                       utility.get_setting('authorization_url'))))
    matches = json.loads(content)['viewedItems']
    try:

        lock = thread.allocate_lock()

        max_threads = 4
        threads = [None] * max_threads
        rets = [None] * max_threads
        video_add_args = []
        size = 0

        i = 0
        for item in matches:
            if(i==max_threads):
#                utility.log('max reached, waiting for join')
                for i in range(len(threads)):
                    threads[i].join()
                    video_add_args.append(rets[i])
                    threads[i] = None
                    rets[i] = None
#                utility.log('all joined')
                i = 0

            threads[i] = threading.Thread(target = view_activity_load_match, args = (item, video_type, lock, rets, i))
            threads[i].start()
#            utility.log('thread '+str(i)+' started')
            size+=1
            if not run_as_widget:
                utility.progress_window(loading_progress, size * 100 / len(matches), 'processing...')

            i+=1

        for i in range(len(threads)):
            if threads[i] != None:
                threads[i].join()
                video_add_args.append(rets[i])
                threads[i] = None
                rets[i] = None
 #       utility.log('all joined')

        for video_add_arg in video_add_args:
            if(video_add_arg != None):
                video_add(video_add_arg)

    except Exception:
        utility.notification(utility.get_string(30306))
        pass
    if utility.get_setting('force_view') and not run_as_widget:
        xbmc.executebuiltin('Container.SetViewMode(' + utility.get_setting('view_id_activity') + ')')
    xbmcplugin.endOfDirectory(plugin_handle)

def view_activity_load_match(item, video_type, lock, rets, i):
    series_id = 0
    is_episode = False
    video_id = unicode(item['movieID'])
    date = item['dateStr']
    try:
        series_id = item['series']
        series_title = item['seriesTitle']
        title = item['title']
        title = series_title + ' ' + title
    except Exception:
        title = item['title']
    title = date + ' - ' + title
    if series_id > 0:
        is_episode = True



    success = False
    while (success == False):
        try:
            ret = video(video_id, title, '', is_episode, False, video_type, '', lock)
            success = True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                time.sleep(2)
            else:
                utility.log('error loading video ' +video_id+'\n'+ traceback.format_exc(), xbmc.LOGERROR)
                break
        except Exception as e:
            utility.log('error loading video ' +video_id+'\n'+ traceback.format_exc(), xbmc.LOGERROR)
            break

    rets[i] = ret


def search(search_string, video_type, run_as_widget=False):
    i = 1
    loading_progress = None
    if not run_as_widget:
        loading_progress = xbmcgui.DialogProgress()
        loading_progress.create('Netflix', utility.get_string(30205) + '...')
        utility.progress_window(loading_progress, 0, '...')
    xbmcplugin.setContent(plugin_handle, 'movies')
    if not xbmcvfs.exists(utility.session_file()):
        login.login()
    post_data = '{"paths":[["search","%s",{"from":0,"to":48},["summary","title"]],["search","%s",["id","length",' \
                '"name","trackIds","requestId"]]],"authURL":"%s"}' % (search_string, search_string,
                                                                      utility.get_setting('authorization_url'))
    content = utility.decode(connect.load_netflix_site(utility.evaluator(), post=post_data))
    try:
        matches = json.loads(content)['value']['videos']
        for k in matches:
            if not run_as_widget:
                utility.progress_window(loading_progress, i * 100 / len(matches), '...')
            video_add(video(unicode(matches[k]['summary']['id']), '', '', False, False, video_type, ''))
            i += 1
        if utility.get_setting('force_view') and not run_as_widget:
            xbmc.executebuiltin('Container.SetViewMode(' + utility.get_setting('view_id_videos') + ')')
        xbmcplugin.endOfDirectory(plugin_handle)
    except Exception:
        utility.notification(utility.get_string(30306))
        pass


def seasons(series_name, series_id, thumb):
    seasons = []
    content = get.series_info(series_id)
    content = json.loads(content)['video']['seasons']
    for item in content:
        seasons.append((item['title'], item['seq']))
    for season in seasons:
        add.season(season[0], season[1], 'list_episodes', thumb, series_name, series_id)
    xbmcplugin.endOfDirectory(plugin_handle)


def episodes(series_id, season):
    xbmcplugin.setContent(plugin_handle, 'episodes')
    content = get.series_info(series_id)
    content = json.loads(content)['video']['seasons']
    for test in content:
        episode_season = unicode(test['seq'])
        if episode_season == season:
            for item in test['episodes']:
                playcount = 0
                episode_id = item['episodeId']
                episode_nr = item['seq']
                episode_title = (unicode(episode_nr) + '. ' + item['title'])
                duration = item['runtime']
                offset = item['bookmark']['offset']
                if (duration > 0 and float(offset) / float(duration)) >= 0.9:
                    playcount = 1
                description = item['synopsis']
                try:
                    thumb = item['stills'][0]['url']
                except:
                    thumb = utility.addon_fanart()
                add.episode(episode_title, episode_id, 'play_video_main', thumb, description, duration, season,
                            episode_nr, series_id, playcount)
    if utility.get_setting('force_view'):
        xbmc.executebuiltin('Container.SetViewMode(' + utility.get_setting('view_id_episodes') + ')')
    xbmcplugin.endOfDirectory(plugin_handle)
