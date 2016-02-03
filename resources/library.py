from __future__ import unicode_literals

import json
import os
import re
import xbmc
import xbmcvfs

import get
from resources import video_parser
from resources.utility import generic_utility


def add_movie(movie_id, title, single_update=True):
    generic_utility.log(title)
    movie_dir, title = get_movie_dir(title)
    if not xbmcvfs.exists(movie_dir+os.sep):
        xbmcvfs.mkdir(movie_dir+os.sep)

    movie_file = generic_utility.clean_filename(title + '.V' + movie_id + 'V' + '.strm', ' .').strip(' .')
    file_handler = xbmcvfs.File(generic_utility.create_pathname(movie_dir.decode('utf-8'), movie_file), 'w')
    file_handler.write(
        generic_utility.encode('plugin://%s/?mode=play_video&url=%s' % (generic_utility.addon_id, movie_id)))
    file_handler.close()
    if generic_utility.get_setting('update_db') == 'true' and single_update:
        xbmc.executebuiltin('UpdateLibrary(video)')
    else:
        xbmc.executebuiltin("Container.Refresh")

def get_movie_dir(title):
    pattern = re.compile('^\d\d.\d\d.\d\d \- .*')
    if pattern.match(title) != None:
        title = title[11:]
    filename = generic_utility.clean_filename(title, ' .')
    movie_dir = xbmc.translatePath(generic_utility.movie_dir() + filename)
    return movie_dir, title


def remove_movie(title):
    movie_dir = get_movie_dir(title)[0]
    xbmcvfs.rmdir(movie_dir+os.sep, force=True)
    if generic_utility.get_setting('update_db') == 'true':
        xbmc.executebuiltin('CleanLibrary(video)')
    else:
        xbmc.executebuiltin("Container.Refresh")


def add_series(series_id, series_title, season, single_update=True):
    series_file = get_series_dir(series_title)
    if not xbmcvfs.exists(series_file+os.sep):
        xbmcvfs.mkdir(series_file+os.sep)
    content = get.series_info(series_id)
    generic_utility.log(str(content))
    content = json.loads(content)['video']['seasons']
    for test in content:
        episode_season = unicode(test['seq'])
        if episode_season == season or season == '':
            season_dir = generic_utility.create_pathname(series_file.decode('utf-8'), test['title'])
            if not xbmcvfs.exists(season_dir+os.sep):
                xbmcvfs.mkdir(season_dir+os.sep)
            for item in test['episodes']:
                episode_id = unicode(item['episodeId'])
                episode_nr = unicode(item['seq'])
                episode_title = item['title']
                if len(episode_nr) == 1:
                    episode_nr = '0' + episode_nr
                season_nr = episode_season
                if len(season_nr) == 1:
                    season_nr = '0' + season_nr
                filename = 'S' + season_nr + 'E' + episode_nr + ' - ' + episode_title + '.V' + episode_id + 'V'+ '.strm'
                filename = generic_utility.clean_filename(filename, ' .')
                file_handler = xbmcvfs.File(generic_utility.create_pathname(season_dir, filename), 'w')
                file_handler.write(
                    generic_utility.encode('plugin://%s/?mode=play_video&url=%s' % (
                    generic_utility.addon_id, episode_id)))
                file_handler.close()
    if generic_utility.get_setting('update_db') == 'true' and single_update:
        xbmc.executebuiltin('UpdateLibrary(video)')
    else:
        xbmc.executebuiltin("Container.Refresh")


def get_series_dir(series_title):
    filename = generic_utility.clean_filename(series_title, ' .')
    series_file = xbmc.translatePath(generic_utility.tv_dir() + filename)
    return series_file


def remove_series(series_title):
    series_file = get_series_dir(series_title)
    xbmcvfs.rmdir(series_file+os.sep, force=True)
    if generic_utility.get_setting('update_db') == 'true':
        xbmc.executebuiltin('CleanLibrary(video)')
    else:
        xbmc.executebuiltin("Container.Refresh")


def update_playcounts():

    videos_data = {}
    videos_data.update(get_movies_data())
    videos_data.update(get_episodes_data())

    if len(videos_data) > 0:
        playback_infos = get.video_playback_info(videos_data)
        videos = json.loads(playback_infos)['value']['videos']
        update_metadatas = []
        playcount_changed = False
        for video_id in videos:
            type = video_parser.parse_type(videos[video_id])
            if type is not 'show':
                playcount = video_parser.parse_duration_playcount(videos[video_id])[1]
                video_data = videos_data[video_id]
                if 'episode_id' in video_data:
                    if video_data['playcount'] != playcount:
                        update_episode_playcount(video_data['episode_id'], playcount)
                        playcount_changed = True
                else:
                    if video_data['playcount'] != playcount:
                        update_movie_playcount(video_data['movie_id'], playcount)
                        playcount_changed = True

        if playcount_changed:
            xbmc.executebuiltin("Container.Refresh")


def update_movie_playcount(movie_id, playcount):
    xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 0, "method": "VideoLibrary.SetMovieDetails", "params": '
                        '{"movieid":%s, "playcount":%s } }' % (movie_id, playcount))


def update_episode_playcount(episode_id, playcount):
    xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 0, "method": "VideoLibrary.SetEpisodeDetails", "params": '
                        '{"episodeid":%s, "playcount":%s } }' % (episode_id, playcount))


def get_movies_data():
    video_data = {}
    ret = generic_utility.decode(xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 0, "method": '
                                                     '"VideoLibrary.GetMovies", '
                                                     '"params": {"properties":["file", "playcount"] } }'))
    jsn = json.loads(ret)
    if 'result' in jsn:
        result = jsn['result']
        if 'movies' in result:
            movies = result['movies']
            for movie in movies:
                regexp_res = re.search('\.V(.*)V\.strm', movie['file'])
                if regexp_res:
                    video_id = regexp_res.group(1)
                    video_data[video_id] = {'movie_id': movie['movieid'], 'playcount': movie['playcount']}
    return video_data


def get_episodes_data():
    video_data = {}
    ret = generic_utility.decode(xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 0, "method": '
                                                     '"VideoLibrary.GetEpisodes", '
                                                     '"params": {"properties":["file", "playcount"] } }'))
    jsn = json.loads(ret)
    if 'result' in jsn:
        result = jsn['result']
        if 'episodes' in result:
            episodes = result['episodes']
            for episode in episodes:
                regexp_res = re.search('\.V(.*)V\.strm', episode['file'])
                if regexp_res:
                    video_id = regexp_res.group(1)
                    video_data[video_id] = {'episode_id': episode['episodeid'], 'playcount': episode['playcount']}

    return video_data
