from __future__ import unicode_literals

from resources.utility import generic_utility

test = False
try:
    import xbmcvfs
except Exception:
    test = True


def write(file_name, content):
#    generic_utility.log('filename: '+file_name)
    if test == False:
        file_handler = xbmcvfs.File(file_name, 'wb')
    else:
        file_handler = open(file_name, 'wb')

    file_handler.write(content)
    file_handler.close()

def read(file_name):
    if test == False:
        file_handler = xbmcvfs.File(file_name, 'rb')
    else:
        file_handler = open(file_name, 'rb')

    content = file_handler.read()
    file_handler.close()
    return content
