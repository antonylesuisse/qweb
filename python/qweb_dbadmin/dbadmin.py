#!/usr/bin/python
# vim:set mouse=:
import glob, os, sys, re

#sys.path[0:0] = glob.glob('lib/QWeb-0.5-py%d.%d.egg'%sys.version_info[:2])+glob.glob('lib/')

import qweb, qweb_static

class DBATable:
	def __init__(self,cols):
		self.cols=cols
		self.hidden=0

class DBACol:
	def __init__(self):
		self.name=None
		self.type=None
		self.hidden=0
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
		for name in dir(mod):
			cls=getattr(mod,name)
			if hasattr(cls, '__mro__'):
				for basecls in cls.__mro__:
					if basecls.__name__=='SQLObject':
						self.pretable(mod, cls)
						self.tables[name]=cls
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
			for order, col in tmp:
				col.dba=DBACol()
				col.dba.name=col.name
				col.dba.nullable=not col.notNone
				col.dba.sqltype=col._sqliteType()
				if col.foreignKey:
					col.dba.longname=getattr(col, 'longname', col.name[:-2].replace('_',' '))
					col.dba.type="many2one"
					col.dba.name=col.name[:-2]
					col.dba.dest=getattr(mod, col.foreignKey)
					col.dba.form="select"
				else:
					col.dba.longname=getattr(col, 'longname', col.name.replace('_',' '))
					col.dba.type="scalar"
				table.dba.cols.append(col)
			table.dba.count=table.select().count()

	def process(self, req):
		path=req.PATH_INFO[len(self.urlroot):]
		if path=="":
			path="index"
		v={}
		if qweb.qweb_control(self, "dbview_" + path, [req,req.REQUEST,req,v]):
			r={}
			r['head']=self.template.render("head",v)
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

		v["body"]=self.template.render("dbview_table_list",v)

	def rowform(self,arg,form,table,row=None,prefix="__"):
		print 'rowform %r'%table
		# denial.consigneeID
		for c in table.dba.cols:
			ca=c.dba
			fn=prefix + ca.name
			# ---------------------------------------------
			# Recurse
			# ---------------------------------------------
			if ca.type=="many2one":
				sub=fn+'__'
				if sub in arg and arg[sub] != 'Cancel':
					fi=qweb.QWebField(sub, default='1')
					form.add_field(fi)
					self.rowform(arg,form,ca.dest,row=None,prefix=sub)
			# ---------------------------------------------
			# Default
			# ---------------------------------------------
			default=""
			if row:
				default=str(getattr(row,ca.name))
				if ca.type=="many2one":
					default=str(getattr(row,ca.name+'ID'))
			elif c.default:
				# TODO
				default=str(c.default)
			# ---------------------------------------------
			# Null
			# ---------------------------------------------
			if c.dba.nullable:
				check=None
			else:
				check="/.+/"
			# ---------------------------------------------
			# Add
			# ---------------------------------------------
			fi=qweb.QWebField(prefix+c.dba.name,default=default,check=check)
			form.add_field(fi)
		return form

	def rowadd(self,form,table,row=None,prefix="__"):
#		v["row"]=v["tableo"](**d)
		pass

	def rowsave(self,form,table,row=None,prefix="__"):
#		v["row"].set(**d)
#		resurce to rowadd
		pass

	def dbview_table_rowadd(self,req,arg,out,v):
		f=v["form"]=qweb.QWebForm()
		self.rowform(arg,f,v["tableo"])
		f.process_input(arg)
		v['pf']='__'
		if arg["save"] and f.valid:
			print "VALID"
			d=f.collect()
			self.rowsave()
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

	# ajouter inline
	def dbview_table_row_edit(self,req,arg,out,v):
		f=v["form"]=qweb.QWebForm()
		self.rowform(arg,f,v["tableo"],v["row"])
		f.process_input(arg)
		v['pf']='__'
		if arg["save"] and f.valid:
			print "VALID"
			d=f.collect()
			self.rowsave()
			print d
			v["saved"]=1
			v["body"]=self.template.render("dbview_table_row_edit",v)
		else:
			v["body"]=self.template.render("dbview_table_row_edit",v)

	def dbview_table_row_del(self,req,arg,out,v):
		v["row"]
		v["body"]="ok"

if __name__ == '__main__':
	pass


