#!/usr/bin/python
# vim:set ts=4 et:
import sys, os, urllib, re, tempfile, urllib2

if len(sys.argv)<2:
    print "usage: vimtrac.py http://hostname/trac/wiki/WikiStart"
    sys.exit()

url=sys.argv[1]
base=os.path.basename(url)
urltxt='%s?format=txt'%url


orig=urllib2.urlopen(urltxt).read()
f=tempfile.NamedTemporaryFile()
f.write(orig)
f.flush()
os.system("%s %s" % (os.getenv("EDITOR", "vi"), f.name))

f.seek(0)
data=f.read()
if data!=orig:

    # POST the file
    urledit='%s?action=edit'%url
    editpage=urllib2.urlopen(urledit).read()

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
        urllib2.urlopen(url,post).read()
        print "%s saved."%url



