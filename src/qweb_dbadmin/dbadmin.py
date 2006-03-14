#!/usr/bin/python
# vim:set mouse=:
import glob, os, sys, re

#sys.path[0:0] = glob.glob('lib/QWeb-0.5-py%d.%d.egg'%sys.version_info[:2])+glob.glob('lib/')

import qweb, qweb_static


class DBATable:
	def __init__(self,cols):
		self.cols=cols

class DBACol:
	def __init__(self):
		self.name=None
		self.type=None
		# many2one
		self.dest=None


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
				c.dba=DBACol()
				c.dba.name=c.name
				c.dba.nullable=not c.notNone
				if c.foreignKey:
					c.dba.type="many2one"
					c.dba.name=c.name[:-2]
					c.dba.dest=getattr(mod,c.foreignKey)
					c.dba.form="select"
				else:
					c.dba.type="scalar"
					c.dba.sqltype="text"
				table.dba.cols.append(c)
			table.dba.count=table.select().count()

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

	def rowform(self,table):
		f=qweb.QWebForm()
		for c in table.dba.cols:
			if c.dba.type=="scalar" or c.dba.type=="many2one":
				if not c.default:
					default=""
				else:
					default=str(c.default)
				if c.dba.nullable:
					check=None
				else:
					check="/.+/"
				fi=qweb.QWebField(c.dba.name,default=default,check=check)
				f.add_field(fi)
		return f
	def rowformedit(self,table,row):
		f=qweb.QWebForm()
		for c in table.dba.cols:
			if c.dba.type=="scalar" or c.dba.type=="many2one":
				default=str(getattr(row,c.dba.name))
				if c.dba.nullable:
					check=None
				else:
					check="/.+/"
				fi=qweb.QWebField(c.dba.name,default=default,check=check)
				f.add_field(fi)
		return f


	def dbview_table_rowadd(self,req,arg,out,v):
		f=v["form"]=self.rowform(v["tableo"])
		f.process_input(arg)
		if arg["save"] and f.valid:
			print "VALID"
			d=f.collect()
			v["row"]=v["tableo"](**d)
			arg.clear()
			return "dbview_table_row_edit"
		else:
			v["body"]=self.template.render("dbview_table_rowadd",v)

	def dbview_table_row(self,req,arg,out,v):
		if not v.has_key("row"):
			res=v["tableo"].select(v["tableo"].q.id==arg["id"])
			if res.count():
				v["row"]=res[0]
			else:
				return "error"

	def dbview_table_row_edit(self,req,arg,out,v):
		f=v["form"]=self.rowformedit(v["tableo"],v["row"])
		f.process_input(arg)
		if arg["save"] and f.valid:
			print " valid"
			req.write("caca ok")
		else:
			print "pas valid"

			req.write(self.template.render("dbview_table_row_edit",v))

	def dbview_table_row_del(self,req,arg,out,v):
		v["row"]
		req.write('ok')

if __name__ == '__main__':
	pass


