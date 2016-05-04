from __future__ import unicode_literals

import json
import re
import traceback
import xbmc
import xbmcgui

from resources import delete
from resources import general
from resources import library
from resources import list
from resources import play
from resources import queue
from resources import search
from resources import connect
from resources.utility import generic_utility

while (generic_utility.get_setting('username') or generic_utility.get_setting('password')) == '':
    generic_utility.open_setting()

generic_utility.prepare_folders()

parameters = generic_utility.parameters_to_dictionary(sys.argv[2])
name = generic_utility.get_parameter(parameters, 'name')
url = generic_utility.get_parameter(parameters, 'url')
mode = generic_utility.get_parameter(parameters, 'mode')
thumb = generic_utility.get_parameter(parameters, 'thumb')
video_type = generic_utility.get_parameter(parameters, 'type')
season = generic_utility.get_parameter(parameters, 'season')
series_id = generic_utility.get_parameter(parameters, 'series_id')
page = generic_utility.get_parameter(parameters, 'page')
run_as_widget = generic_utility.get_parameter(parameters, 'widget') == 'true'
def handle_request():
    try:
        if mode == 'main':
            general.main(video_type)
        elif mode == 'list_videos':
            list.videos(url, video_type, page, run_as_widget)
        elif mode == 'list_seasons':
            list.seasons(name, url, thumb)
        elif mode == 'list_episodes':
            list.episodes(series_id, url)
        elif mode == 'list_genres':
            list.genres(video_type)
        elif mode == 'list_viewing_activity':
            list.viewing_activity(video_type, run_as_widget)
        elif mode == 'add_to_queue':
            queue.add(url)
        elif mode == 'remove_from_queue':
            queue.remove(url)
        elif mode == 'add_movie_to_library':
            library.add_movie(url, name)
        elif mode == 'remove_movie_from_library':
            library.remove_movie(name)
        elif mode == 'add_series_to_library':
            library.add_series(series_id, name, url)
        elif mode == 'remove_series_from_library':
            library.remove_series(name)
        elif mode == 'choose_profile':
            connect.choose_profile()
        elif mode == 'search':
            search.netflix(video_type, url)
        elif mode == 'delete_cookies':
            delete.cookies()
        elif mode == 'delete_cache':
            delete.cache()
        elif mode == 'reset_addon':
            delete.addon()
        elif mode == 'play_video':
            #    utility.log('play_video: '+url)
            play.video(url, series_id);
        elif mode == 'play_video_main':
            #    utility.log('play_video_main: '+url)
            play.video(url, series_id);
        elif mode == 'relogin':
            connect.do_login()
        else:
            general.index()
        return True
    
    except:
        return False

#handle the request, auto retry one time with relogin
success = handle_request()
if not success:
    generic_utility.log('request failed, auto retrying...')
    if connect.do_login() == True:
        success = handle_request()
    else:
        success = False
    
#popup error dialog if still error after retry
if not success:
    generic_utility.log('parameters: ' + sys.argv[2])
    generic_utility.log(traceback.format_exc(), xbmc.LOGERROR)
    dialog = xbmcgui.Dialog()
    dialog.notification(generic_utility.get_string(50003), generic_utility.get_string(50004))
