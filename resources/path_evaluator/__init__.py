import json

from resources.utility import generic_utility


class CacheMissException(Exception):
    def __init__(self, jsn):
        self.jsn = jsn


def req_path(*paths):
    from resources import connect

    auth_url = generic_utility.auth_url()
    api_url = generic_utility.api_url()

    if not auth_url or not api_url:
        connect.do_login()

    post = '{"paths":['
    for curpath in paths:
        post += curpath+','
    post = post[:-1]
    post += '],"authURL":"%s"}' % auth_url

    content = connect.load_netflix_site('%s/pathEvaluator?materialize=true&model=harris' % api_url, post)
    jsn = json.loads(content)
    if 'error' in jsn:
        err = jsn['error']
        if 'innerErrors' in err:
            inners = err['innerErrors']
            for inner_err in inners:
                if 'message' in inner_err:
                    msg = inner_err['message']
                    if 'Map cache miss' == msg:
                        raise CacheMissException(content)
        raise Exception('Invalid path response: ' + content)
    if 'value' not in jsn:
        raise Exception('Invalid path response: ' + content)

    return jsn['value']

def get_root_list_id_from_cookie():
    from resources import connect
    profile = generic_utility.get_setting('selected_profile')

    session = connect.get_netflix_session(False)

    root_list_id = None
    if not profile:
        generic_utility.log('kein profil!')
        for cur_cookie in session.cookies:
            if 'lhpuuidh-browse-' in cur_cookie.name:
#                generic_utility.log('found cookie: '+cur_cookie.value)
                root_list_id = cur_cookie.value
                break
    else:
        for cur_cookie in session.cookies:
            if 'lhpuuidh-browse-'+profile in cur_cookie.name:
                root_list_id = cur_cookie.value
                break

    if not root_list_id:
        raise ValueError('root_list_id not found in cookies!')

    splt = root_list_id.split('%3A')
    if(len(splt) != 3):
        raise ValueError('Invalid split: '+root_list_id)

#    generic_utility.log('root: '+str(splt[2]))
    return splt[2]


def from_to(fromnr, tonr):
    return '{"from":%d,"to":%d}' % (fromnr, tonr)

def path(type, *parms):
    retpath = '['+type+','
    for parm in parms:
        retpath += parm+','
    retpath = retpath[:-1]
    retpath += ']'
    return retpath

def filter_empty(jsn):
    for key in jsn.keys():
        if type(jsn[key]) == dict and '$type' in jsn[key] and jsn[key]['$type'] == 'sentinel':
            del jsn[key]
        elif type(jsn[key]) == dict:
            filter_empty(jsn[key])

def child(chld, jsn):
    if not chld in jsn:
        raise ValueError(str(chld)+' not found in: '+str(jsn))
    return jsn[chld]

def deref(ref, jsn):
    val = jsn
    idx = None
    for layer in ref:
        if not layer in val:
            raise ValueError(str(layer)+' not found in: '+str(jsn))
        val = val[layer]
        idx = layer
    return idx, val
