from __future__ import unicode_literals

import json
import xbmc
import xbmcvfs

import get
from resources.utility import generic_utility


def parse_episode_seasion(match):
    episode = None
    season = None
    if 'summary' in match:
        summary = match['summary']
        episode = get_value(summary, 'episode')
        season = get_value(summary, 'season')

    return episode, season


def video(video_id, is_episode, lock = None, custom_title = None, series_title = None, ignore_cache = False):

    video_details = get.video_info(video_id, lock, ignore_cache = ignore_cache)
    match = json.loads(video_details)['value']['videos'][video_id]

#    generic_utility.log('parsing videodata: '+str(match))

    if custom_title != None:
        title = custom_title
    else:
        title = get_value(match, 'title')

    year = get_value(match, 'releaseYear', '1900')

    thumb_url = extract_thumb_url(match)

    mpaa = get_mpaa(match)

    duration, playcount = parse_duration_playcount(match)

    episode, season = parse_episode_seasion(match)

    type = parse_type(is_episode, match)

    if type == 'tvshow':
        duration = ''

    if generic_utility.get_setting('use_tmdb') == 'true':
        type_tmdb = 'movie' if type =='movie' else 'tv'
        title_tmdb = series_title if series_title != None else title
        load_tmdb_cover_fanart(title_tmdb, video_id, type_tmdb, year)

    description = get_decription(match)
    director = parse_director(match)
    genre = parse_genre(match)

    rating = parse_rating(match)
    movie_metadata = {'title':title, 'video_id':video_id, 'thumb_url': thumb_url, 'type': type, 'description': description, 'duration':duration, 'year':year, 'mpaa':mpaa, \
                      'director':director, 'genre':genre, 'rating':rating, 'playcount':playcount, 'episode' : episode, 'season': season}
#    utility.log(str(video_add_args))
    return movie_metadata


def get_decription(match):
    description = ''
    if 'details' in match:
        m1 = match['details']
        if 'synopsis' in m1:
            description = m1['synopsis']
    return description


def get_mpaa(match):
    mpaa = None
    if 'maturity' in match:
        m1 = match['maturity']
        if 'rating' in m1:
            m2 = m1['rating']
            if 'value' in m2:
                mpaa = m2['value']
    return mpaa


def get_value(match, key, default = None):
    if key in match:
        title = match[key]
    else:
        title = default
    return title


def parse_duration_playcount(match):
    duration = get_value(match, 'runtime', 0)
    playcount = 0

    offset = get_value(match, 'bookmarkPosition', None)
    watched = get_value(match, 'watched', None)

    try:
        if offset:
            if (duration > 0 and float(offset) / float(duration)) >= 0.8:
                playcount = 1
        elif watched:
            playcount = 1
    except Exception:
        generic_utility.log('cannot parse playcount. match: '+str(match))
    return duration, playcount


def parse_rating(match):
    try:
        rating = match['userRating']['average']
    except Exception:
        rating = '0.0'
    return rating


def parse_genre(match):
    try:
        genre = match['details']['genres'][0]['name']
    except Exception:
        genre = ''
    return genre


def parse_director(match):
    try:
        director = match['details']['directors'][0]['name']
    except Exception:
        director = ''
    return director


def parse_type(is_episode, match):
    type = match['summary']['type']
    if type != 'movie':
        if is_episode:
            type = 'episode'
        else:
            type = 'tvshow'
    return type


def extract_thumb_url(match):
    try:
        thumb_url = match['boxarts']['_665x375']['jpg']['url']
    except Exception:
        try:
            thumb_url = match['boxarts']['_342x192']['jpg']['url']
        except Exception:
            thumb_url = generic_utility.addon_fanart()
    return thumb_url


def load_tmdb_cover_fanart(title, video_id, video_type_temp, year):
    year_temp = year
    title_temp = title
    if ' - ' in title_temp:
        title_temp = title_temp[title_temp.index(' - '):]
    filename = video_id + '.jpg'
    filename_none = video_id + '.none'
    cover_file = xbmc.translatePath(generic_utility.cover_cache_dir() + filename)
    cover_file_none = xbmc.translatePath(generic_utility.cover_cache_dir() + filename_none)
    if not (xbmcvfs.exists(cover_file) or xbmcvfs.exists(cover_file_none)):
        generic_utility.log('Downloading cover art. type: %s, video_id: %s, title: %s, year: %s' % (video_type_temp,
                                                                                                    video_id, title_temp,
                                                                                                    year_temp), xbmc.LOGDEBUG)
        get.cover_and_fanart(video_type_temp, video_id, title_temp, year_temp)

