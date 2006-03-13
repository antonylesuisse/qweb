#!/usr/bin/python
# vim:set mouse=:
import glob, os, sys, re

#sys.path[0:0] = glob.glob('lib/QWeb-0.5-py%d.%d.egg'%sys.version_info[:2])+glob.glob('lib/')

import qweb, qweb_static


class DBATable:
	def __init__(self,cols):
		self.cols=cols
class DBACol:
	pass


class DBAdmin:
	def __init__(self,urlroot,mod):
		self.urlroot = urlroot
		self.mod = mod
		self.template = qweb.QWebHtml(qweb_static.get_module_data('qweb_dbadmin','dbadmin.xml'))
		self.tables={}
		self.preprocess(mod)

	def preprocess(self,mod):
		for i in dir(mod):
			c=getattr(mod,i)
			if hasattr(c,'__mro__'):
				for cls in c.__mro__:
					if cls.__name__=='SQLObject':
						self.pretable(mod,c)
						self.tables[i]=c
						break

	# dbview_* attributes
	# dbview_cols cols ordered
	# dbview_cols[0].longname
	# dbview_cols[0].type
	def pretable(self,mod,table):
		if not hasattr(table,'dba'):
			table.dba=DBATable([])
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
				table.dba.cols.append(c)
			# TODO precount
			table.dba.precount=100

	def process(self, req):
		path=req.PATH_INFO[len(self.urlroot):]
		if path=="":
			path="index"
		v={}
		if qweb.qweb_control(self,"dbview_"+path,[req,req.REQUEST,req,v]):
			r={}
			r['head']=v.get('head','')
			r['body']=v.get('body','')
			return r
		else:
			req.http_404()
			return None

	def dbview(self,req,arg,out,v):
		req.response_headers['Content-type'] = 'text/html; charset=UTF-8'
		v['url'] = qweb.QWebURL(self.urlroot, req.PATH_INFO)
	def dbview_index(self,req,arg,out,v):
		v["tables"]=self.tables
		v["body"]=self.template.render("dbview_index",v)
	def dbview_table(self,req,arg,out,v):
		if self.tables.has_key(arg["table"]):
			v["table"]=arg["table"]
			v["tableo"]=self.tables[arg["table"]]
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


