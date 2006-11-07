#!/usr/bin/python
# vim:set ts=4 et:
import sys, os, urllib, re, tempfile, urllib2
import mechanize

url=sys.argv[1]
base=os.path.basename(url)
urltxt='%s?format=txt'%url

orig=urllib2.urlopen(urltxt).read()
data=file(sys.argv[2]).read()

if data!=orig:

    # POST the file
    urledit='%s?action=edit'%url

    br = mechanize.Browser()
    br.set_handle_robots(False)
    br.add_password("http://antony.lesuisse.org/", "ticket", "nospam")
    br.open("http://antony.lesuisse.org/qweb/trac/login")
    br.open(urledit)
    editpage = br.response().read()
    mo=re.search('name="version" value="([^"]+)"',editpage)
    if mo:
        version=mo.group(1)
        post=urllib.urlencode({
            "action":"edit",
            "text":data,
            "version":version,
            "save":"Submit change",
            "author":"anonymous",
            "comment":"" } )
        br.open(url,post)
        br.response().read()
        print "%s saved."%url



