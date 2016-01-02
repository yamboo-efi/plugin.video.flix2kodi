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

    mylist_id = extract_mylist_id(falkor_cache)

    lists = falkor_cache['lists']
    lists = filter_size(lists)
    rets = []
    videos=[]

    list_contains_mylist = False
    for list_key in lists:
        list = lists[list_key]
        list = filter_size(list)
        if 'displayName' in list:
            if list_key == mylist_id:
                list_contains_mylist = True
            display_name = unicode(list['displayName']['value'])
            ret = {'id': list_key, 'name': display_name}
            rets.append(ret)

    if not list_contains_mylist:
        ret = {'id': mylist_id, 'name': generic_utility.get_string(30104)}
        rets.append(ret)

    return rets

def filter_size(lolomos):
    for key in lolomos.keys():
        if key in ('$size', 'size'):
            del lolomos[key]
    return lolomos


def extract_mylist_id(falkor_cache):
    mylist_id = None
    try:
        assert 'lolomos' in falkor_cache
        lolomos = falkor_cache['lolomos']
        filter_size(lolomos)
        assert len(lolomos)==1
        root_list_id = lolomos.keys()[0]
        lists = filter_size(lolomos[root_list_id])
        assert 'mylist' in lists
        mylist_ref = lists['mylist']
        assert len(mylist_ref) == 3
        mylist_idx = mylist_ref[2]
        assert mylist_idx in lists
        mylist = lists[mylist_idx]
        assert len(mylist) == 2
        mylist_id = mylist[1]
    except Exception as ex:
        print('cannot find mylist_id')
        print repr(ex)
    return mylist_id
