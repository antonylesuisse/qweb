#!/usr/bin/python

"""<h1>Tutorial 2 A Complete Demo</h1> """

import array, cgi, fcntl, glob, os, pty, re, signal, select, sys, time

# Optional: Add the QWeb .egg or ../qweb in sys path
sys.path[0:0]=glob.glob('QWeb-*-py%d.%d.egg'%sys.version_info[:2])+glob.glob('../../src')

import qweb, qweb_static

class Terminal:
	def __init__(self,width=80,height=25):
		self.width=width
		self.height=height
		self.scr=array.array('c'," "*width*height)
		self.cx=0
		self.cy=0
	def lineup(self):
		s=self.scr
		h=self.height
		w=self.width
		s[0:w*(h-1)]=s[w:w*h]
		s[w*(h-1):w*h]=array.array('c'," "*w)
	def cdown(self):
		q,r=divmod(self.cy+1,self.height)
		if q:
			self.lineup()
			self.cy=self.height-1
		else:
			self.cy=r
	def cright(self):
		q,r=divmod(self.cx+1,self.width)
		if q:
			self.cdown()
			self.cx=0
		else:
			self.cx=r
	def ctab(self):
		x=self.cx+8
		q,r=divmod(x,8)
		self.cx=(q*8)%self.width
	def cbs(self):
		self.cx=max(0,self.cx-1)
	def echo(self,c):
		self.scr[(self.cy*self.width)+self.cx]=c
		self.cright()
	def write(self,s):
		for i in s:
			if i=="\n":
				self.cdown()
			elif i=="\r":
				self.cx=0
			elif i=="\t":
				self.ctab()
			elif i=="\b":
				self.cbs()
			else:
				self.echo(i)
	def dump(self):
		return self.scr.tostring()
	def __repr__(self):
		r=""
		for i in range(self.height):
			r+=self.scr[self.width*i:self.width*(i+1)].__repr__()+"\n"
		return r

class Process:
	def __init__(self,cmd=['/bin/sh']):
		signal.signal(signal.SIGCHLD, signal.SIG_IGN)
		pid,fd=pty.fork()
		if pid==0:
			os.execv(cmd[0],cmd)
		else:
			self.pid=pid
			self.fd=fd
			self.buf=""
#			fcntl.fcntl(fd, fcntl.F_SETFL, os.O_NONBLOCK)
	def read(self):
		r=""
		while 1:
			i,o,e=select.select( [self.fd], [], [], 0.001)
			if len(i):
				r+=os.read(self.fd,8192)
			else:
				break
#		print "proc:read:%r"%r
		return r
	def write(self,s):
		i,o,e=select.select( [], [self.fd], [], 0.001)
		if len(o):
#			print "proc:write:%r"%s
			os.write(self.fd,s)
		else:
			print "proc:BLOCK:%r"%s

class AjaxTerm:
	def __init__(self):
		self.template = qweb.QWebHtml("ajaxterm.xml")
		self.proc = Process()
		self.term = Terminal()

	def __call__(self, environ, start_response):
		req = qweb.QWebRequest(environ, start_response)
		req.response_gzencode=1
		if req.PATH_INFO.startswith('/test'):
			c=req.REQUEST["a"]
			self.proc.write(c)
			time.sleep(0.001)
			r=self.proc.read()
			self.term.write(r)
			print self.term
			req.write(self.term.dump())
		else:
			v={}
			v['url']=qweb.QWebURL('/',req.PATH_INFO)
			req.write(self.template.render("at_main",v))
		return req
#		qweb.qweb_control(self,'main',[req,req.REQUEST,{}])
		pass

if __name__ == '__main__':
	qweb.qweb_wsgi_autorun(AjaxTerm(),ip='')



