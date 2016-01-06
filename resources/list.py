from __future__ import unicode_literals

import sys
import xbmc
import xbmcgui
import xbmcplugin

import add
import get
from resources import multiprocessor
from resources.utility import generic_utility
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

    if generic_utility.get_setting('force_view') == 'true' and not run_as_widget:
        xbmc.executebuiltin('Container.SetViewMode(' + generic_utility.get_setting('view_id_videos') + ')')
    xbmcplugin.endOfDirectory(plugin_handle)


def viewing_activity(video_type, run_as_widget=False):
    loading_progress = show_loading_progress(run_as_widget)
    xbmcplugin.setContent(plugin_handle, 'movies')

    metadata = get.viewing_activity_matches(video_type)
    if len(metadata) > 0:
        load_videos_to_directory(loading_progress, run_as_widget, metadata, video_type, viewing_activity=True)
    else:
        generic_utility.notification(generic_utility.get_string(30306))

    if generic_utility.get_setting('force_view') and not run_as_widget:
        xbmc.executebuiltin('Container.SetViewMode(' + generic_utility.get_setting('view_id_activity') + ')')
    xbmcplugin.endOfDirectory(plugin_handle)


def add_sort_methods():
    xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_VIDEO_TITLE)
    xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)




def load_videos_to_directory(loading_progress, run_as_widget, metadatas, video_type, page = None, url=None, viewing_activity = False):
    video_metadatas = multiprocessor.load_data(metadatas, video_type, run_as_widget, loading_progress, viewing_activity=viewing_activity)
    removable = url != None and 'my-list' in url

    sorted_video_metadata = sorted(video_metadatas, key=lambda t: t['title'], reverse = viewing_activity)
    for video_metadata in sorted_video_metadata:
        if (video_metadata != None):
            video_add(video_metadata, removable, viewing_activity)
#    generic_utility.log(url)

    items_per_page = int(generic_utility.get_setting('items_per_page'))
    if ((url == None or 'list_viewing_activity' not in url) and len(video_metadatas) == items_per_page):
        add.add_next_item('Next', page + 1, url, video_type, 'list_videos', '')
    if len(video_metadatas) == 0:
        generic_utility.notification(generic_utility.get_string(30306))
    add_sort_methods()

def show_loading_progress(run_as_widget):
    loading_progress = None
    if not run_as_widget:
        loading_progress = xbmcgui.DialogProgress()
        loading_progress.create('Netflix', generic_utility.get_string(30205) + '...')
        generic_utility.progress_window(loading_progress, 0, '...')
    return loading_progress

def video_add(video_metadata, removable = False, viewing_activity = False):
    add.video(video_metadata, removable, viewing_activity = viewing_activity)

def search(search_string, video_type, run_as_widget=False):
    i = 1
    loading_progress = None
    if not run_as_widget:
        loading_progress = xbmcgui.DialogProgress()
        loading_progress.create('Netflix', generic_utility.get_string(30205) + '...')
        generic_utility.progress_window(loading_progress, 0, '...')
    xbmcplugin.setContent(plugin_handle, 'movies')

    video_ids = get.search_matches(search_string, video_type)
    load_videos_to_directory(loading_progress, run_as_widget, video_ids, video_type, 0, '')

    if generic_utility.get_setting('force_view') and not run_as_widget:
        xbmc.executebuiltin('Container.SetViewMode(' + generic_utility.get_setting('view_id_videos') + ')')
    xbmcplugin.endOfDirectory(plugin_handle)


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

    if generic_utility.get_setting('force_view'):
        xbmc.executebuiltin('Container.SetViewMode(' + generic_utility.get_setting('view_id_episodes') + ')')
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

