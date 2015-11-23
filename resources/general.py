from __future__ import unicode_literals

import sys
import xbmcplugin

import add
import login
import utility

plugin_handle = int(sys.argv[1])


def index():
    if login.login():
        add.directory(utility.get_string(30100), '', 'main', '', 'movie')
        add.directory(utility.get_string(30101), '', 'main', '', 'tv')
        add.directory(utility.get_string(30102), '', 'wi_home', '', 'both')
        if not utility.get_setting('single_profile') == 'true':
            add.directory(
                utility.get_string(30103) + ' - [COLOR FF8E0000]' + utility.get_setting('profile_name') + '[/COLOR]',
                '', 'update_displayed_profile', 'DefaultAddonService.png', '', context_enable=False)
        xbmcplugin.endOfDirectory(plugin_handle)


def main(video_type):
    add.directory(utility.get_string(30104), utility.main_url + '/browse/my-list', 'list_videos', '', video_type)
    add.directory(utility.get_string(30105), '', 'list_viewing_activity', '', video_type)
    add.directory(utility.get_string(30106), 'recently-added', 'list_videos', '', video_type)
    if video_type == 'tv':
        add.directory(utility.get_string(30107), utility.main_url + '/browse/genre/83', 'list_videos', '', video_type)
        add.directory(utility.get_string(30108), '', 'list_genres', '', video_type)
    else:
        add.directory(utility.get_string(30108), '', 'list_genres', '', video_type)
    add.directory(utility.get_string(30109), '', 'search', '', video_type)
    xbmcplugin.endOfDirectory(plugin_handle)
