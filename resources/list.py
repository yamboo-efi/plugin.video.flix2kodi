from __future__ import unicode_literals

import sys

import xbmc
import xbmcgui
import xbmcplugin

import add
import get
import utility
from resources import multiprocessor
from resources.video_parser import video

plugin_handle = int(sys.argv[1])


def videos(url, video_type, offset, run_as_widget=False):
    if '' == offset:
        page = 0
    else:
        page = int(offset)

    loading_progress = show_loading_progress(run_as_widget)
    xbmcplugin.setContent(plugin_handle, 'movies')

    video_ids = get.videos_matches(video_type, page, url)
    load_videos_to_directory(loading_progress, run_as_widget, video_ids, video_type, page, url)

    if utility.get_setting('force_view') == 'true' and not run_as_widget:
        xbmc.executebuiltin('Container.SetViewMode(' + utility.get_setting('view_id_videos') + ')')
    xbmcplugin.endOfDirectory(plugin_handle)


def viewing_activity(video_type, run_as_widget=False):
    loading_progress = show_loading_progress(run_as_widget)
    xbmcplugin.setContent(plugin_handle, 'movies')

    metadata = get.viewing_activity_matches(video_type)
    if len(metadata) > 0:
        load_videos_to_directory(loading_progress, run_as_widget, metadata, video_type, viewing_activity=True)
    else:
        utility.notification(utility.get_string(30306))

    if utility.get_setting('force_view') and not run_as_widget:
        xbmc.executebuiltin('Container.SetViewMode(' + utility.get_setting('view_id_activity') + ')')
    xbmcplugin.endOfDirectory(plugin_handle)

def load_videos_to_directory(loading_progress, run_as_widget, metadatas, video_type, page = None, url=None, viewing_activity = False):
    video_metadatas = multiprocessor.load_data(metadatas, video_type, run_as_widget, loading_progress, url, viewing_activity)
    removable = url != None and 'my-list' in url
    for video_metadata in video_metadatas:
        if (video_metadata != None):
            video_add(video_metadata, removable, viewing_activity)
    if (url != None and ('genre' in url or 'recently-added' in url) and len(video_metadatas) > 0):
        add.add_next_item('Next', page + 1, url, video_type, 'list_videos', '')


def show_loading_progress(run_as_widget):
    loading_progress = None
    if not run_as_widget:
        loading_progress = xbmcgui.DialogProgress()
        loading_progress.create('Netflix', utility.get_string(30205) + '...')
        utility.progress_window(loading_progress, 0, '...')
    return loading_progress

def video_add(video_metadata, removable = False, viewing_activity = False):
    add.video(video_metadata, removable, viewing_activity = viewing_activity)

def search(search_string, video_type, run_as_widget=False):
    i = 1
    loading_progress = None
    if not run_as_widget:
        loading_progress = xbmcgui.DialogProgress()
        loading_progress.create('Netflix', utility.get_string(30205) + '...')
        utility.progress_window(loading_progress, 0, '...')
    xbmcplugin.setContent(plugin_handle, 'movies')
    try:
        matches = get.search_matches(search_string)
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
    seasons = get.seasons_data(series_id)
    for season in seasons:
        title, sequence = season
        add.season(title, sequence, thumb, series_name, series_id)
    xbmcplugin.endOfDirectory(plugin_handle)


def episodes(series_id, season):
    xbmcplugin.setContent(plugin_handle, 'episodes')

    episodes = get.episodes_data(season, series_id)
    for episode in episodes:
        add.episode(episode)

    if utility.get_setting('force_view'):
        xbmc.executebuiltin('Container.SetViewMode(' + utility.get_setting('view_id_episodes') + ')')
    xbmcplugin.endOfDirectory(plugin_handle)


def genres(video_type):
    xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_LABEL)

    match = get.genre_data(video_type)

    for genre_id, title in match:
        if video_type == 'tv':
            add.directory(title, 'genre?' + genre_id, 'list_videos', '', video_type)
        elif not genre_id == '83' and video_type == 'movie':
            add.directory(title, 'genre?' + genre_id, 'list_videos', '', video_type)
    xbmcplugin.endOfDirectory(plugin_handle)

