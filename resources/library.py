from __future__ import unicode_literals

import json
import os
import re
import xbmc
import xbmcvfs

import get
from resources import video_parser
from resources.utility import generic_utility
from resources.utility import database


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
    if generic_utility.get_setting('update_db') and single_update:
        xbmc.executebuiltin('UpdateLibrary(video)')


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
    xbmc.executebuiltin('CleanLibrary(video)')

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
    if generic_utility.get_setting('update_db') and single_update:
        xbmc.executebuiltin('UpdateLibrary(video)')


def get_series_dir(series_title):
    filename = generic_utility.clean_filename(series_title, ' .')
    series_file = xbmc.translatePath(generic_utility.tv_dir() + filename)
    return series_file


def remove_series(series_title):
    series_file = get_series_dir(series_title)
    xbmcvfs.rmdir(series_file+os.sep, force=True)
    xbmc.executebuiltin('CleanLibrary(video)')

def update_playcounts():
    tv_dir = xbmc.translatePath(generic_utility.tv_dir())
    movie_dir = xbmc.translatePath(generic_utility.movie_dir())

    video_ids = []
    video_ids.extend(get_video_ids(tv_dir))
    video_ids.extend(get_video_ids(movie_dir))

    if len(video_ids) > 0:
        playback_infos = get.video_playback_info(video_ids)
        videos = json.loads(playback_infos)['value']['videos']
        update_metadatas = []
        for video_id in videos:
            type = video_parser.parse_type(videos[video_id])
            if type is not 'show':
                playcount = video_parser.parse_duration_playcount(videos[video_id])[1]
                update_metadatas.append({'video_id': video_id, 'playcount': playcount})
        if len(update_metadatas) > 0:
            database.update_playcounts(update_metadatas)
            xbmc.executebuiltin("Container.Refresh")

def get_video_ids(directory):
    video_ids = []
    files= []
    for dirpath, dirnames, filenames in os.walk(directory+os.sep):
        for filename in [f for f in filenames if f.decode('utf-8').endswith("V.strm")]:
            files.append(os.path.join(dirpath, filename).decode('utf-8'))

    for curfile in files:
        video_id = re.search('\.V(.*)V\.strm', curfile).group(1)
        video_ids.append(video_id)
    return video_ids