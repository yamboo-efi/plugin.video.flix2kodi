from __future__ import unicode_literals

import sys
import xbmc
import xbmcgui
import xbmcplugin
import json

import add
import get
from resources.path_evaluator.types import lolomos
from resources.utility import generic_utility

plugin_handle = int(sys.argv[1])


def videos(url, video_type, offset, run_as_widget=False):
    if '' == offset:
        page = 0
    else:
        page = int(offset)

    loading_progress = show_loading_progress(run_as_widget)
    xbmcplugin.setContent(plugin_handle, 'movies')

    list_id = None
    genre_id = None
    if 'genre' in url:
        genre_id = url.split('?')[1]
    elif 'list?' in url:
        data = url.split('?')[1]
        if 'mylist' in data:
            root_list = lolomos.get_root_list()
            list_id = lolomos.get_mylist(root_list)[0]
        else:
            list_id = data

    video_metadata = None
    if list_id:
        video_metadata = get.videos_in_list(list_id, page)
    elif genre_id:
        video_metadata = get.videos_in_genre(genre_id, page)

    if video_metadata:
        add_videos_to_directory(loading_progress, run_as_widget, video_metadata, video_type, page, url)

    if generic_utility.get_setting('force_view') == 'true' and not run_as_widget:
        xbmc.executebuiltin('Container.SetViewMode(' + generic_utility.get_setting('view_id_videos') + ')')
    xbmcplugin.endOfDirectory(plugin_handle)


def viewing_activity(video_type, run_as_widget=False):
    loading_progress = show_loading_progress(run_as_widget)
    xbmcplugin.setContent(plugin_handle, 'movies')

    metadata = get.viewing_activity_matches(video_type)
    if len(metadata) > 0:
        add_videos_to_directory(loading_progress, run_as_widget, metadata, video_type, viewing_activity=True)
    else:
        generic_utility.notification(generic_utility.get_string(30306))

    if generic_utility.get_setting('force_view') and not run_as_widget:
        xbmc.executebuiltin('Container.SetViewMode(' + generic_utility.get_setting('view_id_activity') + ')')
    xbmcplugin.endOfDirectory(plugin_handle)


def add_sort_methods():
    xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)
    xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)


def add_videos_to_directory(loading_progress, run_as_widget, video_metadatas, video_type, page = None, url=None, viewing_activity = False):

    removable = url != None and 'mylist' in url
    
    if viewing_activity and type!="movie":
        xbmcplugin.setContent(int(sys.argv[1]), "episodes")
    elif video_type=="movie":
        xbmcplugin.setContent(int(sys.argv[1]), "movies")
    elif video_type == "show":
        xbmcplugin.setContent(int(sys.argv[1]), "tvshows")
    elif video_type == "both":
        xbmcplugin.setContent(int(sys.argv[1]), "tvshows")
    
    if not viewing_activity:
        sorted_video_metadata = sorted(video_metadatas, key=lambda t: t['date_watched'], reverse = viewing_activity)
    else:
        sorted_video_metadata = video_metadatas

    allowed_types = calc_allowed_types(video_type, viewing_activity)

    filtered_video_metadata = []
    for video_metadata in sorted_video_metadata:
        if video_metadata['type'] in allowed_types:
            filtered_video_metadata.append(video_metadata)

    add.videos(filtered_video_metadata, removable, viewing_activity=viewing_activity)

    items_per_page = int(generic_utility.get_setting('items_per_page'))

    if len(video_metadatas) == 0:
        generic_utility.notification(generic_utility.get_string(30306))
    
    if not viewing_activity:
        add_sort_methods()
    else:
        xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_LABEL)
    
    if page is not None and (not url or 'list_viewing_activity' not in url) and len(video_metadatas) == items_per_page:
        add.add_next_item(page + 1, url, video_type, 'list_videos')


def calc_allowed_types(video_type, viewing_activity):
    allowed_types = []
    if video_type == 'both':
        allowed_types.append('movie')
        allowed_types.append('episode')
        allowed_types.append('show')
    elif viewing_activity:
        if video_type == 'movie':
            allowed_types.append('movie')
        else:
            allowed_types.append('episode')
            allowed_types.append('show')
    else:
        allowed_types.append(video_type)
    return allowed_types


def show_loading_progress(run_as_widget):
    loading_progress = None
    if not run_as_widget:
        loading_progress = xbmcgui.DialogProgress()
        loading_progress.create('Netflix', generic_utility.get_string(30205) + '...')
        generic_utility.progress_window(loading_progress, 0, '...')
    return loading_progress


def search(search_string, video_type, run_as_widget=False):
    loading_progress = None
    if not run_as_widget:
        loading_progress = xbmcgui.DialogProgress()
        loading_progress.create('Netflix', generic_utility.get_string(30205) + '...')
        generic_utility.progress_window(loading_progress, 0, '...')
    xbmcplugin.setContent(plugin_handle, 'movies')

    metadatas = get.videos_in_search(search_string)
#    video_ids = get.search_matches(search_string, video_type)
    add_videos_to_directory(loading_progress, run_as_widget, metadatas, video_type, 0, '')

    if generic_utility.get_setting('force_view') and not run_as_widget:
        xbmc.executebuiltin('Container.SetViewMode(' + generic_utility.get_setting('view_id_videos') + ')')
    xbmcplugin.endOfDirectory(plugin_handle)


def seasons(series_name, series_id, thumb):
    xbmcplugin.setContent(plugin_handle, 'seasons')
    seasons = get.seasons_data(series_id)
    for season in seasons:
        add.season(season)
    xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(plugin_handle)


def episodes(series_id, season):
    xbmcplugin.setContent(plugin_handle, 'episodes')
    episodes = get.episodes_data(season, series_id)
    for episode in episodes:
        add.episode(episode)
    
    if generic_utility.get_setting('force_view'):
        xbmc.executebuiltin('Container.SetViewMode(' + generic_utility.get_setting('view_id_episodes') + ')')
    xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_EPISODE)
    xbmcplugin.endOfDirectory(plugin_handle)
    


def genres(video_type):
    xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_LABEL)

    match = get.genre_data(video_type)

    for genre_id, title in match:
        if video_type == 'show':
            add.directory(title, 'genre?' + genre_id, 'list_videos', '', video_type)
        elif not genre_id == '83' and video_type == 'movie':
            add.directory(title, 'genre?' + genre_id, 'list_videos', '', video_type)
    xbmcplugin.endOfDirectory(plugin_handle)


def superbrowse():
    xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_LABEL)

    with open(".kodi/addons/plugin.video.flix2kodi/resources/data/superbrowse_categories.json") as categories_file:
        categories = json.load(categories_file)

    for category_name,category_id in categories.iteritems():
        if 'TV' in category_name:
            video_type='show'
        elif 'Series' in category_name:
            video_tyoe='show'
        else:
            video_type='movie'

        add.directory(category_name, 'genre?' + category_id, 'list_videos', '', video_type)

    xbmcplugin.endOfDirectory(plugin_handle)

