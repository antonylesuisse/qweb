#!/usr/bin/python

"""<h1>Tutorial 2 A Complete Demo</h1> """

import cgi, glob, os, re, sys

# Optional: Add the QWeb .egg or ../qweb in sys path
sys.path[0:0]=glob.glob('QWeb-*-py%d.%d.egg'%sys.version_info[:2])+glob.glob('../src')

import qweb, qweb_static

class QWebDemoApp:

	def __init__(self):
		self.template = qweb.QWebHtml("template.xml")
		self.filetime = os.path.getmtime(__file__)
		self.pages = [i[5:] for i in dir(self) if i.startswith("demo")]
		self.fileserver = qweb_static.StaticDir(urlroot="/static",root=".")

	def __call__(self, environ, start_response):
		# Hack to expire the fcgi
		#if self.filetime != os.path.getmtime(__file__):
		#	environ["wsgi.errors"]._req.server._exit()

		req = qweb.QWebRequest(environ, start_response)

		# Call the qweb control entry to main
		qweb.qweb_control(self,'main',[req,req.REQUEST,{}])

		# return req (req behaves as an iterator with the write buffer)
		return req

	def main(self, req, arg, v):
		if req.PATH_INFO == "" or req.PATH_INFO=="/static":
			req.http_redirect(req.FULL_PATH + '/',1)
			return

		page=req.PATH_INFO[1:].split('/')[0]
		if page=="":
			page="home"

		if page in self.pages:
			return "demo_%s"%page
		else:
			req.http_404()

	def demo(self, req, arg, v):
		v['url']=qweb.QWebURL('/',req.PATH_INFO)

	def demo_home(self, req, arg, v):
		#v["doc"]=re.sub(r"\n([^\n]+)\n---",r"\n<h2>\1</h2>\n",qweb.__doc__)
		v["doc"]=qweb.__doc__
		req.write(self.template.render("demo_home", v))


	def demo_request(self, req, arg, v):
		v["doc"] = qweb.QWebRequest.__doc__.replace("\n\t","\n")
		v["debug"] = req.debug()
		req.write(self.template.render("demo_request", v))

	def demo_session(self, req, arg, v):
		if not req.SESSION.has_key("counter"):
			req.SESSION["counter"]=0
		req.SESSION["counter"]+=1
		v["sess"]=repr(req.SESSION)
		req.write(self.template.render("demo_session", v))

	def demo_template(self, req, arg, v):
		req.write(self.template.render("demo_template", v))

	def demo_form(self, req, arg, v):
		f=v["form"]=self.template.form("demo_form",arg,{'firstname':"John",'sex':'m'})
		if f.valid:
			req.write(self.template.render("demo_formvalid", v))
		else:
			req.write(self.template.render("demo_form", v))

	def demo_static(self, req, arg, v):
		d=self.fileserver.process(req)
		if d:
			v.update(d)
			req.write(self.template.render("demo_static", v))

	# Controller demo
	def demo_control(self, req, arg, v):
		if not req.SESSION.has_key("login"):
			req.SESSION["login"]=None
		v["login"]=req.SESSION["login"]

	def demo_control_home(self, req, arg, v):
		if len(arg["login"]):
			v["login"]=req.SESSION["login"]=arg["login"]
			return "demo_control_logged_page1"
		req.write(self.template.render("demo_control_home", v))

	def demo_control_logout(self, req, arg, v):
		if req.SESSION["login"]:
			req.SESSION["login"]=None
			v["logout"]=1
		return "demo_control_home"

	def demo_control_logged(self, req, arg, v):
		if not req.SESSION["login"]:
			v["loginerror"]=1
			return "demo_control_home"

	def demo_control_logged_page1(self, req, arg, v):
		req.write(self.template.render("demo_control_logged_page1", v))

	def demo_control_logged_page2(self, req, arg, v):
		req.write(self.template.render("demo_control_logged_page2", v))


if __name__ == '__main__':
	qweb.qweb_wsgi_autorun(QWebDemoApp())


