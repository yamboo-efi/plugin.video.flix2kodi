from __future__ import unicode_literals

import json

from resources.utility import generic_utility


def parse_episode_season(match):
    episode = None
    season = None
    if 'summary' in match:
        summary = match['summary']
        episode = get_value(summary, 'episode')
        season = get_value(summary, 'season')

    return episode, season

def parse_video(jsn, video_id):
    title = get_value(jsn, 'title')
    year = get_value(jsn, 'releaseYear', '1900')
    date_watched = get_value(jsn, 'dateStr')
    thumb_url = extract_thumb_url(jsn)
    mpaa = get_mpaa(jsn)
    type = parse_type(jsn)
    # series has no playcount
    if type != 'show': 
        duration, playcount = parse_duration_playcount(jsn)
    else:
        playcount = 0
        duration = ''
    description = get_decription(jsn)
    director = parse_director(jsn)
    genre = parse_genre(jsn)
    rating = parse_rating(jsn)
    movie_metadata = {
        'title': title, 
        'video_id': video_id, 
        'thumb_url': thumb_url, 
        'type': type,
        'description': description, 
        'duration': duration, 
        'year': year, 
        'mpaa': mpaa,
        'director': director, 
        'genre': genre, 
        'rating': rating,
        'playcount': playcount,
        'actors': parse_actors(jsn), 
        'date_watched':date_watched,
        'hd':jsn.get("hd",False)
        }
        
    if type == "episode":
        episode, season = parse_episode_season(jsn)
        movie_metadata["season"] = season
        movie_metadata["episode"] = episode
        movie_metadata["series_title"] = get_value(jsn, 'seriesTitle')
        movie_metadata["series_id"] = get_value(jsn, 'topNodeId')
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
            if (duration > 0 and duration > 0 and float(offset) / float(duration)) >= 0.8:
                playcount = 1
        elif watched:
            playcount = 1
    except Exception:
        generic_utility.log('cannot parse playcount. match: '+str(match))
    return duration, playcount


def parse_rating(match):
    try:
        rating = match['userRating']['average'] * 2
    except Exception:
        rating = '0.0'
    return rating


def parse_genre(match):
    try:
        genres = []
        for item in match['details']['genres']:
            if item.get("name") != "Series":
                genres.append(item.get("name"))
        genre = " / ".join(genres)
    except Exception:
        genre = ''
    return genre

def parse_actors(match):
    actors = []
    try:
        for item in match['details']['actors']:
            actors.append(item.get("name"))
    except Exception:
        pass
    return actors


def parse_director(match):
    try:
        directors = []
        for item in match['details']['directors']:
            directors.append(item.get("name"))
        director = " / ".join(directors)
    except Exception:
        genre = ''
    return director

def parse_type(match):
    type = match['summary']['type']
    if type not in ('movie', 'show', 'episode'):
        generic_utility.error('Unknown type: "'+type+'"')
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
