#!/usr/bin/python

import cgi,glob,os,re,sys

os.chdir(os.path.normpath(os.path.dirname(__file__)))
sys.path[0:0]=glob.glob('../../src')
import qweb, qweb_static

class QWebDemoApp:
	def __call__(self, environ, start_response):
		req=qweb.QWebRequest(environ, start_response)
		qweb_static.StaticZip("/zip","file.zip",ziproot='/static/',listdir=1).process(req,inline=0)
		return req

if __name__ == '__main__':
	qweb.qweb_wsgi_autorun(QWebDemoApp())


