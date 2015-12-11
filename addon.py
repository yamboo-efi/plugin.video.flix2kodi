from __future__ import unicode_literals

from resources import connect
from resources import delete
from resources import general
from resources import library
from resources import list
from resources import play
from resources import profiles
from resources import queue
from resources import search
from resources import utility

utility.log('\n\nStart of plugin')

while (utility.get_setting('username') or utility.get_setting('password')) == '':
    utility.open_setting()

utility.prepare_folders()
connect.new_session()

parameters = utility.parameters_to_dictionary(sys.argv[2])
name = utility.get_parameter(parameters, 'name')
url = utility.get_parameter(parameters, 'url')
mode = utility.get_parameter(parameters, 'mode')
thumb = utility.get_parameter(parameters, 'thumb')
video_type = utility.get_parameter(parameters, 'type')
season = utility.get_parameter(parameters, 'season')
series_id = utility.get_parameter(parameters, 'series_id')
run_as_widget = utility.get_parameter(parameters, 'widget') == 'true'

if mode == 'main':
    general.main(video_type)
elif mode == 'list_videos':
    list.videos(url, video_type, run_as_widget)
elif mode == 'list_seasons':
    list.seasons(name, url, thumb)
elif mode == 'list_episodes':
    list.episodes(series_id, url)
elif mode == 'list_genres':
    list.genres(video_type)
elif mode == 'list_viewing_activity':
    list.view_activity(video_type, run_as_widget)
elif mode == 'add_to_queue':
    queue.add(url)
elif mode == 'remove_from_queue':
    queue.remove(url)
elif mode == 'add_movie_to_library':
    library.movie(url, name)
elif mode == 'add_series_to_library':
    library.series(series_id, name, url)
elif mode == 'play_trailer':
    play.trailer(url, video_type)
elif mode == 'update_displayed_profile':
    profiles.update_displayed()
elif mode == 'search':
    search.netflix(video_type)
elif mode == 'delete_cookies':
    delete.cookies()
elif mode == 'delete_cache':
    delete.cache()
elif mode == 'reset_addon':
    delete.addon()
elif mode == 'play_video_main':
    play.video(url);
else:
    general.index()
