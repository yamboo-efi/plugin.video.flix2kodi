import xmltodict

with open('addon.xml') as fd:
    doc = xmltodict.parse(fd.read())
    print doc['addon']['@version']