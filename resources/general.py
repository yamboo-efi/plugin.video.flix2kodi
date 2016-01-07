from __future__ import unicode_literals

import sys

import xbmcplugin

import add
from resources import connect
from resources.utility import generic_utility
from resources.utility.generic_utility import read_lists

plugin_handle = int(sys.argv[1])





def index():
    add.directory(generic_utility.get_string(30100), '', 'main', '', 'movie', login_context=True)
    add.directory(generic_utility.get_string(30101), '', 'main', '', 'tv', login_context=True)
    add.directory(generic_utility.get_string(30102), '', 'wi_home', '', 'both', login_context=True)
    if not generic_utility.get_setting('single_profile') == 'true':
        add.item(
            generic_utility.get_string(30103) + ' - [COLOR FF8E0000]' + generic_utility.get_setting('profile_name') + '[/COLOR]',
            'choose_profile', login_context=True)
    xbmcplugin.endOfDirectory(plugin_handle)


def add_dynamic_lists(video_type):
    content = connect.load_netflix_site("https://www.netflix.com/")
    falkor_cache = generic_utility.parse_falkorcache(content)

    for list in read_lists(falkor_cache):
        add.directory(list['name'], 'list?'+list['id'], 'list_videos', '', video_type)


def main(video_type):
    add.directory(generic_utility.get_string(30105), '', 'list_viewing_activity', '', video_type)

    add_dynamic_lists(video_type)
    if video_type == 'tv':
        add.directory(generic_utility.get_string(30107), 'genre?83', 'list_videos', '', video_type)
        add.directory(generic_utility.get_string(30108), '', 'list_genres', '', video_type)
    else:
        add.directory(generic_utility.get_string(30108), '', 'list_genres', '', video_type)
    add.directory(generic_utility.get_string(30109), '', 'search', '', video_type)
    xbmcplugin.endOfDirectory(plugin_handle)



