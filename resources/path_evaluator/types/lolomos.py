from resources import path_evaluator
from resources.path_evaluator import from_to, child, deref,filter_empty, req_json_path, get_root_list_id_from_cookie
from resources.utility import generic_utility


def my_list(root_list):
    return path('"%s"' % root_list, '"mylist"')

def lists(root_list, size = 99):
    return path('"%s"' % root_list, from_to(0, size), '"displayName"')

def read_lists(jsn, root_list):
    filter_empty(jsn)
    rets = []

    llms = child('lolomos', jsn)
    rlst = child(root_list, llms)

    if generic_utility.get_setting('is_kid') == 'false':
        mylist = child('mylist', rlst)
        mylist_idx = deref(mylist, jsn)[0]
    else:
        mylist_idx = -1
        mylist_id = None

    for list_ref_idx in rlst:
        list_ref = rlst[list_ref_idx]
        idx, elem = deref(list_ref, jsn)
        if list_ref_idx == mylist_idx:
            mylist_id = idx

        if 'displayName' in elem:
            display_name = unicode(elem['displayName'])
            ret = {'id': idx, 'name': display_name}
            rets.append(ret)

    return mylist_id, rets

def get_root_list():
    return get_root_list_id_from_cookie()
#    root_list = '-1'

#    jsn = req_path(lists(root_list, 1))
#    llms = child('lolomos', jsn)
#    assert len(llms) == 2
#    for key in llms:
#        if key != '-1':
#            root_list_id = key
#            break
#    return root_list_id

def get_mylist(root_list_id):
    ret = req_json_path(my_list(root_list_id), lists(root_list_id))
    llms = child('lolomos', ret)
    rlst = child(root_list_id, llms)
    mylist_ref1 = child('mylist', rlst)
    mylist_ref2 = deref(mylist_ref1, ret)[1]
    mylist = deref(mylist_ref2, ret)
    return mylist


def path(*parms):

    return path_evaluator.path('"lolomos"', *parms)
