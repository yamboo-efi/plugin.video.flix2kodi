from __future__ import unicode_literals

import json
import xbmc
import xbmcvfs

import get
import utility


def movie(movie_id, title, single_update=True):
    filename = utility.clean_filename(title + '.strm', ' .').strip(' .')
    movie_file = xbmc.translatePath(utility.movie_dir() + filename)
    file_handler = xbmcvfs.File(movie_file, 'w')
    file_handler.write(utility.encode('plugin://%s/?mode=play_video&url=%s' % (utility.addon_id, movie_id)))
    file_handler.close()
    if utility.get_setting('update_db') and single_update:
        xbmc.executebuiltin('UpdateLibrary(video)')


def series(series_id, series_title, season, single_update=True):
    filename = utility.clean_filename(series_title, ' .')
    series_file = xbmc.translatePath(utility.tv_dir() + filename)
    if not xbmcvfs.exists(series_file):
        xbmcvfs.mkdir(series_file)
    content = get.series_info(series_id)
    content = json.loads(content)['video']['seasons']
    for test in content:
        episode_season = unicode(test['seq'])
        if episode_season == season or season == '':
            season_dir = utility.create_pathname(series_file, test['title'])
            if not xbmcvfs.exists(season_dir):
                xbmcvfs.mkdir(season_dir)
            for item in test['episodes']:
                episode_id = unicode(item['episodeId'])
                episode_nr = unicode(item['seq'])
                episode_title = item['title']
                if len(episode_nr) == 1:
                    episode_nr = '0' + episode_nr
                season_nr = episode_season
                if len(season_nr) == 1:
                    season_nr = '0' + season_nr
                filename = 'S' + season_nr + 'E' + episode_nr + ' - ' + episode_title + '.strm'
                filename = utility.clean_filename(filename, ' .')
                file_handler = xbmcvfs.File(utility.create_pathname(season_dir, filename), 'w')
                file_handler.write(
                    utility.encode('plugin://%s/?mode=play_video&url=%s' % (utility.addon_id, episode_id)))
                file_handler.close()
    if utility.get_setting('update_db') and single_update:
        xbmc.executebuiltin('UpdateLibrary(video)')
