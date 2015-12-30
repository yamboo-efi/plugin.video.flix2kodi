from __future__ import unicode_literals

import re
import time
import xbmc
import xbmcvfs
import json

import login
import search
from resources import utility, connect

def videos_matches(video_type, page, url):
    post_data = ''
    video_ids = []
    if not xbmcvfs.exists(utility.cookies_file()):
        login.login()
    target_url = utility.evaluator()

    items_per_page = int(utility.get_setting('items_per_page'))
    off_from = page * items_per_page
    off_to = off_from + items_per_page - 2

    if 'recently-added' in url:
        post_data = utility.recently_added % (off_from, off_to, utility.get_setting('authorization_url'))
    elif 'genre' in url:
        #        utility.log('from:' + str(off_from)+' to: '+str(off_to))
        post_data = utility.genre % (url.split('?')[1], off_from, off_to, utility.get_setting('authorization_url'))
    elif 'my-list' in url:
        post_data = None
        target_url = utility.mylist_url
    response = connect.load_netflix_site(target_url, post=post_data)
#    utility.log('response: '+response)
    if 'my-list' in url:
        extract_my_list_video_ids(response, video_ids, video_type)
    else:
        video_ids = extract_other_video_ids(response, video_ids)
    return video_ids


def extract_other_video_ids(response, video_ids):
    content = response
    jsondata = json.loads(content)
#    utility.log('jsondata: ' + str(jsondata))
    if 'videos' in jsondata['value']:
        video_ids = jsondata['value']['videos']
    return video_ids


def extract_my_list_video_ids(response, video_ids, video_type):
    match = re.compile('netflix.falkorCache = ({.*});</script><script>window.netflix', re.DOTALL | re.UNICODE).findall(
        response)
    content = match[0]
    jsondata = json.loads(content)
    if 'videos' in jsondata:
        videos = jsondata['videos']
        utility.log(unicode(videos))
        for video in videos:
            if not video in ('$size', 'size'):
                video_id = video
                metadata_type = get_metadata_type_my_list(video, videos)
                utility.log('type: ' + metadata_type)

                if video_type == metadata_type:
                    video_ids.append(video_id)


def get_metadata_type_my_list(video, videos):
    type = 'unknown'
    if 'summary' in videos[video]:
        summary = videos[video]['summary']
        if 'type' in summary:
            type = summary['type']

    if 'movie' == type:
        metadata_type = 'movie'
    elif 'unknown' == type:
        metadata_type = 'unknown'
    else:
        metadata_type = 'tv'

    return metadata_type


def viewing_activity_matches(video_type):
    if not xbmcvfs.exists(utility.cookies_file()):
        login.login()
    content = viewing_activity_info()
    matches = json.loads(content)['viewedItems']

    metadata = []
    utility.log('activity: '+unicode(matches))
    for match in matches:
        utility.log(match)

        if 'seriesTitle' in match:
            metadata_type = 'tv'
            series_title = match['seriesTitle']
        else:
            metadata_type = 'movie'
            series_title = None

        if video_type == metadata_type:
            metadata.append({'id':unicode(match['movieID']), 'title':get_viewing_activity_title(match), 'series_title':series_title})

    return metadata

def get_viewing_activity_title(item):
    date = item['dateStr']
    try:
        series_id = item['series']
        series_title = item['seriesTitle']
        title = item['title']
        title = series_title + ' ' + title
    except Exception:
        title = item['title']
    title = date + ' - ' + title
    return title

def seasons_data(series_id):
    seasons = []
    content = series_info(series_id)
    utility.log(str(content))
    content = json.loads(content)['video']['seasons']
    for item in content:
        season = item['title'], item['seq']
        seasons.append(season)
    return seasons


def episodes_data(season, series_id):
    episodes = []

    content = series_info(series_id)
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


def search_matches(search_string):
    if not xbmcvfs.exists(utility.cookies_file()):
        login.login()
    content = search_results(search_string)
    matches = json.loads(content)['value']['videos']
    return matches


def genre_data(video_type):
    match = []
    if not xbmcvfs.exists(utility.cookies_file()):
        login.login()

    content = genre_info(video_type)

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


def video_info(video_id, lock = None):
    content = ''
    cache_file = xbmc.translatePath(utility.cache_dir() + video_id + '.cache')
    if xbmcvfs.exists(cache_file):
        file_handler = xbmcvfs.File(cache_file, 'rb')
        content = utility.decode(file_handler.read())
        file_handler.close()
    if not content:
        post_data = utility.video_info % (video_id, video_id, video_id, video_id,
                                         utility.get_setting('authorization_url'))
        content = connect.load_netflix_site(utility.evaluator(), post=post_data, lock = lock)
        file_handler = xbmcvfs.File(cache_file, 'wb')
        file_handler.write(utility.encode(content))
        file_handler.close()
    return content


def series_info(series_id):
    content = ''
    cache_file = xbmc.translatePath(utility.cache_dir() + series_id + '_episodes.cache')
    if xbmcvfs.exists(cache_file) and (time.time() - xbmcvfs.Stat(cache_file).st_mtime() < 60 * 5):
        file_handler = xbmcvfs.File(cache_file, 'rb')
        content = utility.decode(file_handler.read())
        file_handler.close()
    if not content:
        url = utility.series_url % (utility.get_setting('api_url'), series_id)
        content = connect.load_netflix_site(url)
        file_handler = xbmcvfs.File(cache_file, 'wb')
        file_handler.write(utility.encode(content))
        file_handler.close()
    return content


def cover_and_fanart(video_type, video_id, title, year):
    content = search.tmdb(video_type, title, year)
    if content['total_results'] > 0:
        content = content['results'][0]

        poster_path = content['poster_path']
        if poster_path:
            cover_url = utility.picture_url + poster_path
            cover(video_id, cover_url)

        backdrop_path = content['backdrop_path']
        if backdrop_path:
            fanart_url = utility.picture_url + backdrop_path
            fanart(video_id, fanart_url)


def fanart(video_id, fanart_url):
    filename = video_id + '.jpg'
    fanart_file = xbmc.translatePath(utility.fanart_cache_dir() + filename)
    try:
        content_jpg = connect.load_other_site(fanart_url)
        file_handler = open(fanart_file, 'wb')
        file_handler.write(content_jpg)
        file_handler.close()
    except Exception:
        pass


def cover(video_id, cover_url):
    filename = video_id + '.jpg'
    filename_none = video_id + '.none'

    cover_file = xbmc.translatePath(utility.cover_cache_dir() + filename)
    cover_file_none = xbmc.translatePath(utility.cover_cache_dir() + filename_none)

    try:
        content_jpg = connect.load_other_site(cover_url)
        file_handler = open(cover_file, 'wb')
        file_handler.write(content_jpg)
        file_handler.close()
    except Exception:
        file_handler = open(cover_file_none, 'wb')
        file_handler.write('')
        file_handler.close()
        pass


def trailer(video_type, title):
    content = search.tmdb(video_type, title)
    if content['total_results'] > 0:
        content = content['results'][0]
        tmdb_id = content['id']
        content = search.trailer(video_type, tmdb_id)
    else:
        utility.notification(utility.get_string(30305))
        content = None
    return content


def genre_info(video_type):
    post_data = ''
    if video_type == 'tv':
        post_data = utility.series_genre % utility.get_setting('authorization_url')
    elif video_type == 'movie':
        post_data = utility.movie_genre % utility.get_setting('authorization_url')
    else:
        pass
    content = connect.load_netflix_site(utility.evaluator(), post=post_data)
    return content


def search_results(search_string):
    post_data = '{"paths":[["search","%s",{"from":0,"to":48},["summary","title"]],["search","%s",["id","length",' \
                '"name","trackIds","requestId"]]],"authURL":"%s"}' % (search_string, search_string,
                                                                      utility.get_setting('authorization_url'))
    content = connect.load_netflix_site(utility.evaluator(), post=post_data)
    return content


def viewing_activity_info():
    content = connect.load_netflix_site(utility.activity_url % (utility.get_setting('api_url'),
                                                                               utility.get_setting(
                                                                                   'authorization_url')))
    return content