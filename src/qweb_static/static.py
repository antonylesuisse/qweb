#!/usr/bin/python2.3
# vim:set noet ts=4 foldlevel=0:

# TODO support ranges

"""A QWeb Component to serve static content

Serve static contents, directories, zipfiles or python modules

"""

import calendar,cgi,md5,mimetypes,os,stat,sys,time,urllib,zipfile

def get_module_data(module,path):
	m=sys.modules[module]
	l=getattr(m,'__loader__',None)
	d=os.path.dirname(m.__file__)
	fname=os.path.join(d,path)
	if l:
		return l.get_data(fname)
	else:
		return file(fname).read()

def path_clean(path):
	path=path.replace('\\','/')
	pl=[i for i in path.split('/') if (i!='..' and i!='')]
	return '/'.join(pl)

class Entry:
	def  __init__(self,path,type,mtime,size,data=None):
		self.path=path
		self.name=os.path.basename(path)
		self.type=type
		self.mtime=mtime
		self.size=size
		self.data=data

class StaticBase:
	def __init__(self, urlroot="/", listdir=1):
		self.urlroot=urlroot
		self.listdir=listdir

		self.type_map=mimetypes.types_map.copy()
		self.type_map['.csv']='text/csv'
		self.type_map['.htm']='text/html; charset=UTF-8'
		self.type_map['.html']='text/html; charset=UTF-8'
		self.type_map['.svg']='image/svg+xml'
		self.type_map['.svgz']='image/svg+xml'
		self.gzencode={".css":1, ".js":1, ".htm":1, ".html":1, ".txt":1, ".xml":1}

	def serve_dir(self,req,path):
		if not req.PATH_INFO.endswith('/'):
			uri = req.FULL_PATH + '/'
			req.http_redirect(uri,1)
		else:
			l=self.fs_listdir(path)
			l.sort()
			body='<h1>Listing directory '+path+'</h1><a href="..">..</a><br>\n'
			for i in l:
				name=i.name
				if i.type=="dir":
					name+='/'
				body+='<a href="%s">%s</a><br>\n'%(name,name)
			return body
	def serve_file(self,req,path,entry):
		if req.SESSION!=None:
			req.SESSION.session_limit_cache=0
		lastmod=time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(entry.mtime))
		etag=md5.new(lastmod).hexdigest()
		req.response_headers['Last-Modified']=lastmod
		req.response_headers['ETag']=etag
		# cached output
		if lastmod==req.environ.get('HTTP_IF_MODIFIED_SINCE',"") or etag==req.environ.get('HTTP_IF_NONE_MATCH',""):
			req.response_status='304 Not Modified'
		# normal output
		else:
			ext = os.path.splitext(path)[1].lower()
			ctype = self.type_map.get(ext, 'application/octet-stream')
			req.response_headers['Content-Type']=ctype
			if entry.data!=None:
				f=entry.data
			else:
				f=self.fs_getfile(path)
				if not isinstance(f,str):
					f=f.read()
			if self.gzencode.has_key(ext):
				req.response_gzencode=1
			req.response_headers['Content-Length']=str(len(f))
			req.write(f)
	def process(self, req, inline=1):
		path=path_clean(req.PATH_INFO[len(self.urlroot):])
		e=self.fs_stat(path)
		if e:
			if e.type=="dir" and self.listdir:
				body=self.serve_dir(req, path)
				if inline:
					return {'head':"",'body':body}
				else:
					req.write(body)
			elif e.type=="file":
				self.serve_file(req,path,e)
		else:
			req.http_404()

class StaticDir(StaticBase):
	def __init__(self, urlroot="/", root=".", listdir=1):
		self.root=root
		StaticBase.__init__(self,urlroot,listdir)
	def fs_stat(self,path):
		fs_path = os.path.join(self.root,path)
		try:
			st = os.stat(fs_path)
			if stat.S_ISDIR(st.st_mode):
				type="dir"
			else:
				type="file"
			return Entry(path,type,st.st_mtime,st.st_size)
		except os.error:
			return None
	def fs_getfile(self,path):
		fs_path = os.path.join(self.root,path)
		return file(fs_path,'rb')
	def fs_listdir(self,path):
		fs_path = os.path.join(self.root,path)
		return [self.fs_stat(os.path.join(fs_path,i)) for i in os.listdir(fs_path)]

class StaticZip(StaticBase):
	def __init__(self, urlroot="/", zipname="",ziproot="/", listdir=1):
		StaticBase.__init__(self,urlroot,listdir)
		self.zipfile=zipfile.ZipFile(zipname)
		self.zipmtime=os.path.getmtime(zipname)
		self.ziproot=path_clean(ziproot)
		self.zipdir={}
		self.zipentry={}

		for zi in self.zipfile.infolist():
			self.zipentry[zi.filename]=Entry(zi.filename,"file",self.zipmtime,zi.file_size)

		if listdir:
			# Build a directory index
			for k,v in self.zipentry.items():
				d=os.path.dirname(k)
				n=os.path.basename(k)
				if d in self.zipdir:
					self.zipdir[d][n]=v
				else:
					self.zipdir[d]={n:v}
				i=d
				while len(i):
					d=os.path.dirname(i)
					n=os.path.basename(i)
					e=Entry(i,"dir",self.zipmtime,0)
					if d in self.zipdir:
						self.zipdir[d][n]=e
					else:
						self.zipdir[d]={n:e}
					i=d
	def fs_stat(self,path):
		fs_path=os.path.join(self.ziproot,path)
		if fs_path in self.zipentry:
			return self.zipentry[fs_path]
		elif fs_path in self.zipdir:
			return Entry(path,"dir",self.zipmtime,0)
		else:
			return None
	def fs_getfile(self,path):
		fs_path = self.ziproot[1:]+path
		return self.zipfile.read(fs_path)
	def fs_listdir(self,path):
		fs_path = self.ziproot[1:]+path
		return self.zipdir[fs_path].values()

class StaticModule(StaticBase):
	def __init__(self, urlroot="/", module="", module_root="/", listdir=0):
		StaticBase.__init__(self,urlroot,listdir)
		self.module=module
		self.mtime=time.time()
		self.module_root=path_clean(module_root)
	def fs_stat(self,path):
		name=os.path.join(self.module_root,path)
		try:
			d=get_module_data(self.module,name)
			e=Entry(path,"file",self.mtime,len(d))
			e.data=d
			return e
		except IOError,e:
			return None

#----------------------------------------------------------
# OLD version: Pure WSGI
#----------------------------------------------------------
class WSGIStaticServe:
	def __init__(self, urlroot="/", root=".", listdir=1, banner=''):
		self.urlroot=urlroot
		self.root="."
		self.listdir=listdir
		self.banner=banner
		self.type_map=mimetypes.types_map.copy()
		self.type_map['.csv']='text/csv'
	def __call__(self, environ, start_response):
		pi=environ.get("PATH_INFO","")
		path = os.path.normpath("./" + pi[len(self.urlroot):] )
		if sys.platform=="win32":
			path="/".join(path.split('\\'))
		assert path[0]!='/'
		fullpath = os.path.join(self.root, path)
		if os.path.isdir(fullpath) and self.listdir:
			# redirects for directories
			if not pi.endswith('/'):
				uri = urllib.quote(environ["SCRIPT_NAME"] + environ["PATH_INFO"]) + '/'
				start_response("301 Moved Permanently", [("Content-type", "text/html"),("Location",uri)])
				return []
			body=self.banner
			body+='<h1>Listing directory '+path+'</h1><a href="..">..</a><br>\n'
			l=os.listdir(fullpath)
			l.sort()
			for i in l:
				if os.path.isdir(os.path.join(fullpath,i)):
					body+='<a href="%s/">%s/</a><br>\n'%(i,i)
				else:
					body+='<a href="%s">%s</a><br>\n'%(i,i)
			start_response("200 OK", [("Content-type", "text/html")])
			return [body]
		elif os.path.isfile(fullpath):
			f = open(fullpath,'rb')
			ext = os.path.splitext(fullpath)[1].lower()
			ctype = self.type_map.get(ext,'application/octet-stream')
			start_response("200 OK", [("Content-type", ctype)])
			return [f.read()]
		else:
			start_response("404 Not Found", [("Content-type", "text/html")])
			return ['<h1>404 Not Found</h1>']


#
