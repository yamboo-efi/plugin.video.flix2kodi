import json
import re

import xbmc
import xbmcvfs

import connect
import get
import login
import utility


def get_videos_matches(page, url):
    post_data = ''
    matches = []
    if not xbmcvfs.exists(utility.session_file()):
        login.login()
    target_url = utility.evaluator()
    off_from = page * 6
    off_to = off_from + 4

    if 'recently-added' in url:
        post_data = utility.recently_added % (off_from, off_to, utility.get_setting('authorization_url'))
    elif 'genre' in url:
        #        utility.log('from:' + str(off_from)+' to: '+str(off_to))
        post_data = utility.genre % (url.split('?')[1], off_from, off_to, utility.get_setting('authorization_url'))
    elif 'my-list' in url:
        post_data = None
        target_url = utility.mylist_url
    response = connect.load_netflix_site(target_url, post=post_data)
    #    utility.log(response)
    if 'my-list' in url:
        match = re.compile('netflix.falkorCache = ({.*});</script><script>window.netflix', re.DOTALL).findall(response)
        content = match[0]
        jsondata = json.loads(content)
        if 'videos' in jsondata:
            videos = jsondata['videos']
            for video in videos:
                if not video in ('$size', 'size'):
                    matches.append(video)
    else:
        content = response
        jsondata = json.loads(content)
        #        utility.log(str(jsondata))
        if 'videos' in jsondata['value']:
            matches = jsondata['value']['videos']
    return matches


def video(video_id, title, thumb_url, is_episode, hide_movies, video_type, url, lock = None):
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

    rating = None
    try:
        rating = match['userRating']['average']
    except Exception:
        pass

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


def get_viewing_activity_matches():
    if not xbmcvfs.exists(utility.session_file()):
        login.login()
    content = get.viewing_activity_info()
    matches = json.loads(content)['viewedItems']
    return matches


def get_seasons_data(series_id):
    seasons = []
    content = get.series_info(series_id)
    utility.log(str(content))
    content = json.loads(content)['video']['seasons']
    for item in content:
        season = item['title'], item['seq']
        seasons.append(season)
    return seasons


def load_episodes_data(season, series_id):
    episodes = []

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

                episode = series_id, episode_id, episode_title, description, episode_nr, season, duration, thumb, playcount
                episodes.append(episode)
    return episodes


def load_search_matches(search_string):
    if not xbmcvfs.exists(utility.session_file()):
        login.login()
    content = get.search_results(search_string)
    matches = json.loads(content)['value']['videos']
    return matches


def load_genre_data(video_type):
    match = []
    if not xbmcvfs.exists(utility.session_file()):
        login.login()

    content = get.genre_info(video_type)

    matches = json.loads(content)['value']['genres']
    for item in matches:
        try:
            match.append((unicode(matches[item]['id']), matches[item]['menuName']))
        except Exception:
            try:
                match.append((unicode(matches[item]['summary']['id']), matches[item]['summary']['menuName']))
            except Exception:
                pass
    return match
