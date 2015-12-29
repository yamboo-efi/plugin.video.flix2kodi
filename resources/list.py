from __future__ import unicode_literals

import sys

import xbmc
import xbmcgui
import xbmcplugin

import add
import utility
from resources import multiprocessor
from resources.video_parser import get_videos_matches, video, \
    get_viewing_activity_matches, get_seasons_data, load_episodes_data, load_search_matches, load_genre_data

plugin_handle = int(sys.argv[1])


def videos(url, video_type, offset, run_as_widget=False):
    if '' == offset:
        page = 0
    else:
        page = int(offset)

    loading_progress = None
    if not run_as_widget:
        loading_progress = xbmcgui.DialogProgress()
        loading_progress.create('Netflix', utility.get_string(30205) + '...')
        utility.progress_window(loading_progress, 0, '...')
    xbmcplugin.setContent(plugin_handle, 'movies')

    matches = get_videos_matches(page, url)
    video_add_args = multiprocessor.load_data(matches, video_type, run_as_widget, loading_progress, url)

    for video_add_arg in video_add_args:
        if(video_add_arg != None):
            video_add(video_add_arg)

    if ('genre' in url or 'recently-added' in url) and len(video_add_args) > 0:
        add.add_next_item('Next', page + 1, url, video_type, 'list_videos', '')

    if utility.get_setting('force_view') == 'true' and not run_as_widget:
        xbmc.executebuiltin('Container.SetViewMode(' + utility.get_setting('view_id_videos') + ')')
    xbmcplugin.endOfDirectory(plugin_handle)


def video_add(args):
    title, video_id, next_mode, thumb_url, type, description, duration, year, mpaa, director, genre, rating, playcount, remove = args
    add.video(title, video_id, next_mode, thumb_url, type, description, duration, year, mpaa,
                  director, genre, rating, playcount, remove=remove)


def viewing_activity(video_type, run_as_widget=False):
    loading_progress = None
    if not run_as_widget:
        loading_progress = xbmcgui.DialogProgress()
        loading_progress.create('Netflix', utility.get_string(30205) + '...')
        utility.progress_window(loading_progress, 0, '...')
    xbmcplugin.setContent(plugin_handle, 'movies')

    matches = get_viewing_activity_matches()
    try:

        video_add_args = multiprocessor.load_data(matches, video_type, run_as_widget, loading_progress, viewing_activity=True)

        for video_add_arg in video_add_args:
            if(video_add_arg != None):
                video_add(video_add_arg)

    except Exception:
        utility.notification(utility.get_string(30306))
        pass
    if utility.get_setting('force_view') and not run_as_widget:
        xbmc.executebuiltin('Container.SetViewMode(' + utility.get_setting('view_id_activity') + ')')
    xbmcplugin.endOfDirectory(plugin_handle)


def search(search_string, video_type, run_as_widget=False):
    i = 1
    loading_progress = None
    if not run_as_widget:
        loading_progress = xbmcgui.DialogProgress()
        loading_progress.create('Netflix', utility.get_string(30205) + '...')
        utility.progress_window(loading_progress, 0, '...')
    xbmcplugin.setContent(plugin_handle, 'movies')
    try:
        matches = load_search_matches(search_string)
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
    seasons = get_seasons_data(series_id)
    for season in seasons:
        title, sequence = season
        add.season(title, sequence, thumb, series_name, series_id)
    xbmcplugin.endOfDirectory(plugin_handle)


def episodes(series_id, season):
    xbmcplugin.setContent(plugin_handle, 'episodes')

    episodes = load_episodes_data(season, series_id)
    for episode in episodes:
        add.episode(episode)

    if utility.get_setting('force_view'):
        xbmc.executebuiltin('Container.SetViewMode(' + utility.get_setting('view_id_episodes') + ')')
    xbmcplugin.endOfDirectory(plugin_handle)


def genres(video_type):
    xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_LABEL)

    match = load_genre_data(video_type)

    for genre_id, title in match:
        if video_type == 'tv':
            add.directory(title, 'genre?' + genre_id, 'list_videos', '', video_type)
        elif not genre_id == '83' and video_type == 'movie':
            add.directory(title, 'genre?' + genre_id, 'list_videos', '', video_type)
    xbmcplugin.endOfDirectory(plugin_handle)

