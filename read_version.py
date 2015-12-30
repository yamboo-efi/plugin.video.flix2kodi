import xmltodict

with open('plugin.video.flix2kodi/addon.xml') as fd:
    doc = xmltodict.parse(fd.read())
    print doc['addon']['@version']