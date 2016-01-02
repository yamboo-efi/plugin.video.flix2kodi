from __future__ import unicode_literals

import sys
import xbmcplugin

import add
from resources import connect
from resources.utility import generic_utility

plugin_handle = int(sys.argv[1])





def index():
    add.directory(generic_utility.get_string(30100), '', 'main', '', 'movie', login_context=True)
    add.directory(generic_utility.get_string(30101), '', 'main', '', 'tv', login_context=True)
    add.directory(generic_utility.get_string(30102), '', 'wi_home', '', 'both', login_context=True)
    if not generic_utility.get_setting('single_profile') == 'true':
        add.directory(
            generic_utility.get_string(30103) + ' - [COLOR FF8E0000]' + generic_utility.get_setting('profile_name') + '[/COLOR]',
            '', 'update_displayed_profile', 'DefaultAddonService.png', '', context_enable=False)
    xbmcplugin.endOfDirectory(plugin_handle)


def add_dynamic_lists(video_type):
    content = connect.load_netflix_site("https://www.netflix.com/")
    falkor_cache = generic_utility.parse_falkorcache(content)

    for list in read_lists(falkor_cache):
        add.directory(list['name'], 'list?'+list['id'], 'list_videos', '', video_type)

    pass


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



def read_lists(falkor_cache):
    lists = falkor_cache['lists']
    lists = filter_size(lists)
    rets = []
    videos=[]
    for list_key in lists:
        list = lists[list_key]
        list = filter_size(list)
        if 'displayName' in list:
            display_name = unicode(list['displayName']['value'])
            ret = {'id': list_key, 'name': display_name}
            rets.append(ret)
    return rets

def filter_size(lolomos):
    for key in lolomos.keys():
        if key in ('$size', 'size'):
            del lolomos[key]
    return lolomos
