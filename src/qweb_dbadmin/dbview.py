#!/usr/bin/python
# vim:set mouse=:
import glob, os, sys, re

#sys.path[0:0] = glob.glob('lib/QWeb-0.5-py%d.%d.egg'%sys.version_info[:2])+glob.glob('lib/')

import qweb, qweb_static

class DBAdmin:
	def __init__(self,urlroot,mod):
		self.urlroot = urlroot
		self.mod = mod
		s = qweb_static.get_module_data('qweb_dbadmin','dbview.xml')
		self.template = qweb.QWebHtml(s)

	def premodel(self,mod):
		for i in dir(mod):
			c=getattr(mod,i)
			if hasattr(c,'sqlmeta'):
				self.pretable(mod,c)

	# dbview_* attributes
	# dbview_cols cols ordered
	# dbview_cols[0].longname
	# dbview_cols[0].type
	def pretable(self,mod,table):
		if not hasattr(table,'dbview'):
			table.dbview_cols=[]
			tmp=[(col.creationOrder, col) for col in table.sqlmeta.columns.values() if col.name!='childName']
			tmp.sort()
			for order,c in tmp:
				if not hasattr(c,'longname'):
					c.longname=c.name
				if c.foreignKey:
					c.dbview_name=c.name[:-2]
					c.dbview_type="many2one"
					c.dbview_dest=getattr(mod,c.foreignKey)
					c.dbview_form="select"
				else:
					c.dbview_name=c.name
					c.dbview_type="normal"
					# TODO precise type
					c.dbview_form="text"
					#c.dbview_form_text_machin
					#c.dbview_form_text_machin
				table.dbview_cols.append(c)
			# TODO precount
			table.dbview_precount=100
			table.dbview=1

	def process(self, req):
		pass
#		mtime=os.path.getmtime("dbview.xml")
#		if self.mtime!=mtime:
#			self.mtime=mtime
#			self.template = QWebHtml("dbview.xml")
#		if len(req.PATH_INFO)<=1:
#			req.http_redirect('/index',1)
#		elif qweb_control(self,"dbview_"+req.PATH_INFO,[req,req.REQUEST,req,{}]):
#			pass
#		else:
#			r = self.file_server.process(req)
#			if r:
#				req.write(r["body"])
#		return req




	def dbview(self,req,arg,out,v):
		req.response_headers['Content-type'] = 'text/html; charset=UTF-8'
		v['url'] = QWebURL('/', req.PATH_INFO)
	def dbview_index(self,req,arg,out,v):
		req.write('<a href="table_list?table=Country">test</a>')
	def dbview_table(self,req,arg,out,v):
		v["module"]=model
		if hasattr(model,arg["table"]):
			v["table"]=arg["table"]
			v["tableo"]=getattr(model,arg["table"])
			# if getattr(mol) instranceof SQLobject
			self.pretable(v["module"],v['tableo'])
		else:
			return "error"
	def dbview_table_list(self,req,arg,out,v):
		v["start"]=arg.int("start")
		v["search"]=arg["search"]
		v["step"]=arg.int("step")
		v["order"]=arg.get("order","id")
		if v["step"]==0:
			v["step"]=50
		res=v["tableo"].select(orderBy=v["order"])
		v["total"]=res.count()
		v["rows"]=res[v["start"]:v["start"]+v["step"]]
		req.write(self.template.render("dbview_table_list",v))
	def dbview_table_rowadd(self,req,arg,out,v):
		v["row"]=v["tableo"]()
		return "dbview_table_row_edit"
	def dbview_table_row(self,req,arg,out,v):
		if not v.has_key("row"):
			res=v["tableo"].select(v["tableo"].q.id==arg["id"])
			if res.count():
				v["row"]=res[0]
			else:
				return "error"
	def dbview_table_row_edit(self,req,arg,out,v):
		req.write(self.template.render("dbview_table_row_edit",v))
	def dbview_table_row_del(self,req,arg,out,v):
		v["row"]
		req.write('ok')

if __name__ == '__main__':
	pass


