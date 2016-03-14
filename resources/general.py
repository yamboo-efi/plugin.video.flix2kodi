from __future__ import unicode_literals

import sys

import xbmcplugin

import add
from resources import connect
from resources.path_evaluator.types import lolomos
from resources.utility import generic_utility
from resources.path_evaluator import req_path, CacheMissException, child

plugin_handle = int(sys.argv[1])





def index():
    add.directory(generic_utility.get_string(30100), '', 'main', '', 'movie', login_context=True)
    add.directory(generic_utility.get_string(30101), '', 'main', '', 'show', login_context=True)

    add.directory(generic_utility.get_string(30102), '', 'main', '', 'dynamic', login_context=True)

    if not generic_utility.get_setting('single_profile') == 'true':
        add.item(
            generic_utility.get_string(30103) + ' - [COLOR FF8E0000]' + generic_utility.get_setting('profile_name') + '[/COLOR]',
            'choose_profile', login_context=True)
    xbmcplugin.endOfDirectory(plugin_handle)



def main(video_type):
    add.directory(generic_utility.get_string(30105), '', 'list_viewing_activity', '', video_type)

    if video_type == 'show':
        add.directory(generic_utility.get_string(30107), 'genre?83', 'list_videos', '', video_type)
        add.directory(generic_utility.get_string(30108), '', 'list_genres', '', video_type)

    elif video_type == 'movie':
        add.directory(generic_utility.get_string(30108), '', 'list_genres', '', video_type)
    elif video_type == 'dynamic':
        add_dynamic_lists()

    if video_type != 'dynamic' and generic_utility.get_setting('is_kid') == 'false':
        root_list = lolomos.get_root_list()
        mylist = lolomos.get_mylist(root_list)
        add.directory(child('displayName', mylist[1]), 'list?&mylist', 'list_videos', '', video_type)

    add.directory(generic_utility.get_string(30109), '', 'search', '', video_type)
    xbmcplugin.endOfDirectory(plugin_handle, cacheToDisc=False)



def add_dynamic_lists():

    ret, root_list = req_lists()
    mylist_id, lists = lolomos.read_lists(ret, root_list)
    for list in lists:
        list_id = list['id']
        mylist_parm = ''
        if list_id == mylist_id:
            mylist_parm = '&mylist'

        add.directory(list['name'], 'list?' + list_id+mylist_parm, 'list_videos', '', 'both')


def req_lists():
    try:
        root_list = lolomos.get_root_list()
        ret = req_path(lolomos.my_list(root_list), lolomos.lists(root_list))
    except CacheMissException:
        connect.refresh_data()
        root_list = lolomos.get_root_list()
        ret = req_path(lolomos.my_list(root_list), lolomos.lists(root_list))
    return ret, root_list
