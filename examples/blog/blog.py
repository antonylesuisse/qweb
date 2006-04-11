#!/usr/bin/python2.3
# vim:set noet foldlevel=0:

import StringIO,cPickle,csv,datetime,email.Header,email.MIMEText,glob,os,quopri,random,re,sets,shutil,socket,sys,time,zipfile

sys.path[0:0]=glob.glob('lib/*.egg')+glob.glob('../../src')

import sqlobject as so
import qweb

#---------------------------------------------------------
# Sqlobject init
#---------------------------------------------------------
so.sqlhub.processConnection = so.connectionForURI('sqlite:'+os.path.realpath('database.db')+'?debug=False')
so.sqlhub.processConnection = so.connectionForURI('sqlite:'+os.path.realpath('database.db'))

#---------------------------------------------------------
# Databases
#---------------------------------------------------------
class post(so.SQLObject):
	ctime = so.DateTimeCol(notNone=1,default=so.DateTimeCol.now)
	title = so.StringCol(length=128, notNone=1,default='')
	body = so.StringCol(notNone=1,default='')
	comments = so.MultipleJoin('comment')

class comment(so.SQLObject):
	post = so.ForeignKey('post', notNone=1)
	ctime = so.DateTimeCol(notNone=1,default=so.DateTimeCol.now)
	name = so.StringCol(length=128, notNone=1,default='')
	email = so.StringCol(length=128, notNone=1,default='')
	title = so.StringCol(length=128, notNone=1,default='')
	body = so.StringCol(notNone=1,default='')

def so2dict(row):
	d={}
	for n in row.sqlmeta.columns:
		d[n]=str(getattr(row,n))
	return d

def initdb():
	for i in [post,comment]:
		i.dropTable(ifExists=True)
		i.createTable()
	for i in range(10):
		p=post(title='Post %d'%(i+1))
		for j in range(5):
			comment(post=p,title='comment %d on post %d'%(j+1,i+1))

#---------------------------------------------------------
# Web interface
#---------------------------------------------------------
class BlogApp:
	# Called once per fcgi process, or only once for commandline
	def __init__(self):
		self.t = qweb.QWebHtml("template.xml")

	# Called for each request
	def __call__(self, environ, start_response):
		req = qweb.QWebRequest(environ, start_response)

		if req.PATH_INFO=="/":
			page='blog_home'
		else:
			page="blog"+req.PATH_INFO

		mo=re.search('blog/post_view/([0-9]+)',page)
		if mo:
			page='blog/post_view'
			req.REQUEST['post']=mo.group(1)

		if not qweb.qweb_control(self,page,[req,req.REQUEST,{}]):
			req.http_404()

		return req

	def blog(self, req, arg, v):
		v['url']=qweb.QWebURL("/",req.PATH_INFO)

	def blog_home(self, req, arg, v):
		v['posts'] = post.select(orderBy="-id")[:5]
		req.write(self.t.render("home", v))

	def blog_postlist(self, req, arg, v):
		v["posts"] = post.select()
		req.write(self.t.render("postlist", v))

	def blog_postadd(self, req, arg, v):
		v["post"] = post()
		return "blog_post_edit"

	# Ensure that all blog_post_* handlers have a valid 'post' argument
	def blog_post(self, req, arg, v):
		if not "post" in v:
			try:
				v['post'] = post.get(arg.int('post'))
			except Exception,e:
				req.write(str(e))
				return 'error'

	def blog_post_view(self, req, arg, v):
		req.write(self.t.render("post_view", v))

	def blog_post_edit(self, req, arg, v):
		f=v["form"]=self.t.form("post_edit",arg,so2dict(v["post"]))
		if f.valid:
			v["post"].set(**f.collect())
		req.write(self.t.render("post_edit", v))

if __name__=='__main__':
	initdb()
	b=BlogApp()
	qweb.qweb_wsgi_autorun(b,threaded=0)

