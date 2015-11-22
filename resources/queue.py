from __future__ import unicode_literals

import xbmc

import connect
import utility

'''
this urls don't exists anymore
new api call
{"callPath":["lolomos","8dfdsfdsf0e-7sdf-4dfds-bsdf-sdfdsfsdfsd4_ROOT","addToList"],"params":["8dfdsfdsf0e-7sdf-4dfds-bsdf-sdfdsfsdfsd4_2781780",2,["videos",70171942],14170287,null,null],"paths":[],"pathSuffixes":[[["length","trackIds","context","displayName"]],[{"to":3}],["watchedEvidence",{"to":2}]],"authURL":""}
rewrite necessary :(
'''


def add(id):
    if authMyList:
        encodedAuth = urllib.urlencode({'authURL': authMyList})
        load(urlMain + "/AddToQueue?movieid=" + id + "&qtype=INSTANT&" + encodedAuth)
        xbmc.executebuiltin('XBMC.Notification(NetfliXBMC:,' + str(translation(30144)) + ',3000,' + icon + ')')
    else:
        debug("Attempted to addToQueue without valid authMyList")


def remove(id):
    if authMyList:
        encodedAuth = urllib.urlencode({'authURL': authMyList})
        load(urlMain + "/QueueDelete?" + encodedAuth + "&qtype=ED&movieid=" + id)
        xbmc.executebuiltin('XBMC.Notification(NetfliXBMC:,' + str(translation(30145)) + ',3000,' + icon + ')')
        xbmc.executebuiltin("Container.Refresh")
    else:
        debug("Attempted to removeFromQueue without valid authMyList")
