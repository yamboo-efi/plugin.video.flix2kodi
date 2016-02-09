from __future__ import unicode_literals

import json
import time

import collections

from resources.path_evaluator import path, from_to, req_path, filter_empty, child, deref

test = False
try:
    import xbmc
    import xbmcvfs
except Exception:
    test = True

from resources import connect, video_parser
from resources.utility import generic_utility
if generic_utility.android():
    from resources.android import ordered_dict_backport

video_infos1 = '["availability","bookmarkPosition","details","episodeCount","maturity",' \
               '"queue","releaseYear","requestId","runtime","seasonCount","summary","title","userRating","watched"]'
video_infos2 = '"current",["summary","runtime","bookmarkPosition","creditsOffset","title"]'
video_infos3 = '"seasonList","current",["showMemberType","summary"]'
video_infos4 = '"boxarts",["_665x375","_342x192"],"jpg"'


def viewing_activity_matches(video_type):
    content = viewing_activity_info()
    matches = json.loads(content)['viewedItems']

    if generic_utility.android():
        metadatas = ordered_dict_backport.OrderedDict()
    else:
        metadatas = collections.OrderedDict()
    videos_str = ''
    for match in matches:
        if 'seriesTitle' in match:
            metadata_type = 'show'
            series_title = match['seriesTitle']
        else:
            metadata_type = 'movie'
            series_title = None

        video_id = unicode(match['movieID'])
        if video_type == metadata_type:
            metadatas[video_id] = {'title': get_viewing_activity_title(match), 'series_title': series_title}
            videos_str += video_id + ','

    videos_str = videos_str[:-1]
    path1 = path('"videos"', '[' + videos_str + ']', video_infos1)
    path2 = path('"videos"', '[' + videos_str + ']', video_infos2)
    path3 = path('"videos"', '[' + videos_str + ']', video_infos3)
    path4 = path('"videos"', '[' + videos_str + ']', video_infos4)
    ret = req_path(path1, path2, path3, path4)
    filter_empty(ret)
    videos = child('videos', ret)
    rets = []

    for video_id in metadatas:
        vjsn = videos[video_id]
        video_metadata = metadatas[video_id]
        title = video_metadata['title']
        series_title = video_metadata['series_title']
        parsed = video_parser.parse_video(title, vjsn, series_title, video_id)
        rets.append(parsed)

    return rets


def videos_in_list(list_to_browse, page):
    items_per_page = int(generic_utility.get_setting('items_per_page'))
    off_from = page * items_per_page
    off_to = off_from + items_per_page - 2

    path1 = path('"lists"', '"' + list_to_browse + '"', from_to(off_from, off_to), video_infos1)
    path2 = path('"lists"', '"' + list_to_browse + '"', from_to(off_from, off_to), video_infos2)
    path3 = path('"lists"', '"' + list_to_browse + '"', from_to(off_from, off_to), video_infos3)
    path4 = path('"lists"', '"' + list_to_browse + '"', from_to(off_from, off_to), video_infos4)
    ret = req_path(path1, path2, path3, path4)
    filter_empty(ret)
    lists = child('lists', ret)
    list = child(list_to_browse, lists)
    rets = []
    for ref in list:
        video_id, vjsn = deref(list[ref], ret)
        parsed = video_parser.parse_video(None, vjsn, None, video_id)
        rets.append(parsed)
    return rets

def videos_in_genre(genre_to_browse, page):
    items_per_page = int(generic_utility.get_setting('items_per_page'))
    off_from = page * items_per_page
    off_to = off_from + items_per_page - 2
    path1 = path('"genres"', '"' + genre_to_browse + '"', '"su"', from_to(off_from, off_to), video_infos1)
    path2 = path('"genres"', '"' + genre_to_browse + '"', '"su"', from_to(off_from, off_to), video_infos2)
    path3 = path('"genres"', '"' + genre_to_browse + '"', '"su"', from_to(off_from, off_to), video_infos3)
    path4 = path('"genres"', '"' + genre_to_browse + '"', '"su"', from_to(off_from, off_to), video_infos4)
    ret = req_path(path1, path2, path3, path4)
    filter_empty(ret)
    gnrs = child('genres', ret)
    gnre = child(genre_to_browse, gnrs)
    sus = child('su', gnre)
    rets = []
    for ref in sus:
        video_id, vjsn = deref(sus[ref], ret)
        parsed = video_parser.parse_video(None, vjsn, None, video_id)
        rets.append(parsed)
    return rets

def videos_in_search(search_str):
    path1 = path('"search"', '"' + search_str + '"', from_to(0,99), video_infos1)
    path2 = path('"search"', '"' + search_str + '"', from_to(0,99), video_infos2)
    path3 = path('"search"', '"' + search_str + '"', from_to(0,99), video_infos3)
    path4 = path('"search"', '"' + search_str + '"', from_to(0,99), video_infos4)
    ret = req_path(path1, path2, path3, path4)
    filter_empty(ret)
    search = child('search', ret)
    search_node = child(search_str, search)

    rets = []
    for video_ref in search_node:
        video_id, vjsn = deref(search_node[video_ref], ret)
        parsed = video_parser.parse_video(None, vjsn, None, video_id)
        rets.append(parsed)
    return rets


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
    #    utility.log(str(content))
    content = json.loads(content)['video']['seasons']
    for item in content:
        season = item['title'], item['seq']
        seasons.append(season)
    return seasons

def season_title(series_id, seq):
    title = None
    datas = seasons_data(series_id)
    for data in datas:
        if data[1] == seq:
            title = data[0]
            break;
    return title


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
                    thumb = generic_utility.addon_fanart()
                #                generic_utility.log('episode-title: '+episode_title)
                episode = series_id, episode_id, episode_title, description, episode_nr, season, duration, thumb, playcount
                episodes.append(episode)
    return episodes



def genre_data(video_type):
    match = []

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


def series_info(series_id):
    content = ''
    cache_file = xbmc.translatePath(generic_utility.cache_dir() + series_id + '_episodes.cache')
    if xbmcvfs.exists(cache_file) and (time.time() - xbmcvfs.Stat(cache_file).st_mtime() < 60 * 5):
        file_handler = xbmcvfs.File(cache_file, 'rb')
        content = generic_utility.decode(file_handler.read())
        file_handler.close()
    if not content:
        url = generic_utility.series_url % (generic_utility.get_setting('api_url'), series_id)
        content = connect.load_netflix_site(url)
        file_handler = xbmcvfs.File(cache_file, 'wb')
        file_handler.write(generic_utility.encode(content))
        file_handler.close()
    return content


def cover_and_fanart(video_type, video_id, title, year):
    import search
    content = search.tmdb(video_type, title, year)
    if content['total_results'] > 0:
        content = content['results'][0]

        poster_path = content['poster_path']
        if poster_path:
            cover_url = generic_utility.picture_url + poster_path
            cover(video_id, cover_url)

        backdrop_path = content['backdrop_path']
        if backdrop_path:
            fanart_url = generic_utility.picture_url + backdrop_path
            fanart(video_id, fanart_url)


def fanart(video_id, fanart_url):
    filename = video_id + '.jpg'
    fanart_file = xbmc.translatePath(generic_utility.fanart_cache_dir() + filename)
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

    cover_file = xbmc.translatePath(generic_utility.cover_cache_dir() + filename)
    cover_file_none = xbmc.translatePath(generic_utility.cover_cache_dir() + filename_none)

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
    import search
    content = search.tmdb(video_type, title)
    if content['total_results'] > 0:
        content = content['results'][0]
        tmdb_id = content['id']
        content = search.trailer(video_type, tmdb_id)
    else:
        generic_utility.notification(generic_utility.get_string(30305))
        content = None
    return content


def genre_info(video_type):
    post_data = ''
    if video_type == 'show':
        post_data = generic_utility.series_genre % generic_utility.get_setting('authorization_url')
    elif video_type == 'movie':
        post_data = generic_utility.movie_genre % generic_utility.get_setting('authorization_url')
    else:
        pass
    content = connect.load_netflix_site(generic_utility.evaluator(), post=post_data)
    return content


def viewing_activity_info():
    content = connect.load_netflix_site(generic_utility.activity_url % (generic_utility.get_setting('api_url'),
                                                                        generic_utility.get_setting(
                                                                                'authorization_url')))
    return content


def video_playback_info(video_datas):
    ids_str = ''
    for video_data in video_datas:
        ids_str += '"'+video_data+'",'
    ids_str = ids_str[:-1]
    post_data = generic_utility.video_playback_info % (ids_str, generic_utility.get_setting('authorization_url'))
    content = connect.load_netflix_site(generic_utility.evaluator(), post=post_data)
    return content


def track_id_list(list):
    jsn = req_path(path('"lists"', '"%s"' % list, '"trackIds"'))
    lsts = child('lists', jsn)
    lst = child(list, lsts)
    track_ids = child('trackIds', lst)
    track_id = child('trackId', track_ids)
    return track_id
